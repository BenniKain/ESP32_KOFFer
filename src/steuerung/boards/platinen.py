from machine import freq, Pin, I2C
import machine
import utime
import network
from dht import DHT11
from hx711 import HX711
from bmp180 import BMP180
from ssd1306 import SSD1306_I2C
from src.steuerung.methoden import Datenlesen, Steuersetup, Oledanzeige, Relay
import uasyncio as asyncio
import gc
import ujson as json


class Board():

    config_dir = "src/static/configs/"
    network_file = '/src/static/configs/networks.json'
    completeDict = {"STA_Name": "--", "STA_IP": "--"}
    datenDict = {"temp": "--", "hum": "--",
                 "tBMP": "--", "press": "--", }
    ventilqueueList = []
    logfile = "/loggingdata/loggingfiles.txt"
    kofferDict = {}

    screenfeld = 1  # für bildschirme zum iterieren von anzeigen
    screenfelder = [i for i in range(1, 5)]

    def __init__(self, boardname) -> None:
        self.erstelle_ConfigFiles()
        self.config = self.get_config(boardname)
        self.configEsp = self.get_ESP_Config()
        self.sommerzeit = self.configEsp["sommerzeit"]
        self.configPins = self.config["Pins"]
        self.configSensoren = self.config["SENSOREN"]
        self.i2c = I2C(scl=Pin(self.configPins["I2C_scl"]),
                       sda=Pin(self.configPins["I2C_sda"]), freq=400000)
        self.pumpenrelay = Relay(self.configPins["pumpenrelay"])
        #self.pumpentaster = Pin(self.configPins["pumpentaster"], Pin.IN)
        self.dht11 = DHT11(Pin(self.configPins["dht11"]))  # inits DHT sensor
        self.get_anzeige()
        # self.start_HX711()
        self.start_BMP()
        self.start_OLED()
        # self.set_Sensor_calGerade()

    def erstelle_ConfigFiles(self):
        cfile = self.config_dir+"defaultconfig.json"
        with open(cfile, "r") as f:
            confFiles = json.loads(f.read())
        for file in confFiles["defaultConfig"]:
            try:
                print(file)
                f = open(self.config_dir+ "custom"+file, "r")
            except:  # open failed
                with open(self.config_dir+file, "r") as f:
                    lines = json.loads(f.read())
                with open(self.config_dir+"custom"+file, "w") as newf:
                    json.dump(lines,newf)  # TODO

    def set_Sensor_calGerade(self):
        bmpCal = self.configSensoren["BMP180"]
        self.bmp180.TcalOffset = bmpCal["T lowVal soll"]-bmpCal["T lowVal ist"]
        self.bmp180.TcalSteigung = (
            bmpCal["T highVal soll"]-bmpCal["T highVal ist"])/self.bmp180.TcalOffset
        self.bmp180.PcalOffset = bmpCal["P lowVal soll"]-bmpCal["P lowVal ist"]
        self.bmp180.PcalSteigung = (
            bmpCal["P highVal soll"]-bmpCal["P highVal ist"])/self.bmp180.PcalOffset

        dht11Cal = self.configSensoren["DHT11"]
        self.dht11.TcalOffset = dht11Cal["T lowVal soll"] - \
            dht11Cal["T lowVal ist"]
        self.dht11.TcalSteigung = (
            dht11Cal["T highVal soll"]-dht11Cal["T highVal ist"])/self.dht11.TcalOffset
        self.dht11.humcalOffset = dht11Cal["hum lowVal soll"] - \
            dht11Cal["hum lowVal ist"]
        self.dht11.humcalSteigung = (
            dht11Cal["hum highVal soll"]-dht11Cal["hum highVal ist"])/self.dht11.humcalOffset

    async def updateJSON(self):
        while True:
            datenfile = self.config_dir+"data.json"
            with open(datenfile, "w") as jsonfile:
                json.dump(self.datenDict, jsonfile)

            ventilqueue = self.config_dir+"ventilqueue.json"
            jsfile = {"ventilqueue": self.ventilqueueList}
            with open(ventilqueue, "w") as jsonfile:
                json.dump(jsfile, jsonfile)

            await asyncio.sleep(2)

    def set_time(self):
        try:
            import ntptime
            ntptime.settime()  # set the rtc datetime from the remote server geht eine stunde falsch wegen zeitverschiebung. rtc.dattime nimmt komisches argument, nicht geschafft
            t = utime.localtime(utime.mktime(utime.localtime()) + 3600)
            print(t)
        except:
            pass

    def get_ESP_Config(self):
        config_file = self.config_dir+"espconfig.json"
        with open(config_file, "r") as jsonfile:
            data = json.loads(jsonfile.read())
        for knownesp in data["known_ESP"]:
            if knownesp["espID"] == self.get_espID:
                return knownesp

        data["known_ESP"].append({"espID": self.get_espID, "espType": "esp32",
                                  "name": "Default_Koffer",
                                  "mode": "Koffer",
                                  "sommerzeit": "True"})
        with open(config_file, "w") as jsonfile:
            json.dump(data, jsonfile)
        return self.get_ESP_Config()

    def get_config(self, boardname):
        config_file = self.config_dir+"boardconfig.json"
        with open(config_file, "r") as jsonfile:
            data = json.loads(jsonfile.read())
        return data[boardname]

    def get_anzeige(self):
        self.anzeigeschalter = Pin(
            self.configPins["anzeigeschalter"], Pin.IN, Pin.PULL_DOWN)
        self.anzeigeschalter.irq(
            trigger=Pin.IRQ_RISING, handler=self.anzeigeInterrupt)

    def start_HX711(self):
        try:
            # setzt die frequenz der maschine auf den wert für hx711 waage laut beschreibung
            self.freq = freq(160000000)
            self.hx711 = HX711(pd_sck=self.configPins["hx711_sck"],
                               dout=self.configPins["hx711_dout"])
            self.hx711.SCALING_FACTOR = self.config["HX711"]["SCALING_FACTOR"]
            self.waagenTaste = Pin(
                self.configPins["waagenTaste"], Pin.IN, Pin.PULL_DOWN)
            self.waagenTaste.irq(trigger=Pin.IRQ_RISING,
                                 handler=self.waagentarInterrupt)
            self.hx711Active = True

        except Exception as e:
            print("Starten der HX711 Waage fehlgeschlagen: ", e)
            self.hx711Active = False
            
    async def waagenanzeige(self):
        while True:
            print("HX711 value from waagenanzeige", self.hx711.read())
            await asyncio.sleep(1)

    def waagentarInterrupt(self, Pin):
        print("Tare:", self.hx711.tare())
        utime.sleep(0.1)

    def start_BMP(self):
        try:
            self.bmp180 = BMP180(self.i2c)
            print("BMP180 gestartet")

            return True
        except Exception as e:
            print("BMP180 nicht gestartet: ", e)

            return False

    def start_OLED(self):
        try:
            self.oled = SSD1306_I2C(128, 64, self.i2c)
        except Exception as e:
            pass
        # print("Error Oled Display: rebooting now...\t", e)

    @property
    def get_STA(self):
        if network.WLAN(network.STA_IF).active():
            STA_IP = network.WLAN(network.STA_IF).ifconfig()[
                0]  # ip ist verbundene sta
            STA_Name = network.WLAN(network.STA_IF).config("essid")
        else:
            STA_IP, STA_Name = "--", "--"

        self.completeDict.update({"STA_IP": STA_IP, "STA_Name": STA_Name})
        return STA_IP, STA_Name

    @property
    def get_AP(self):
        if network.WLAN(network.AP_IF).active():
            AP_IP = network.WLAN(network.AP_IF).ifconfig()[
                0]  # ip ist accesspoint
            AP_Name = network.WLAN(network.AP_IF).config("essid")
        else:
            AP_IP, AP_Name = "--", "--"

        self.completeDict.update({"AP_IP": AP_IP, "AP_Name": AP_Name})
        return AP_IP, AP_Name

    async def updateIPs(self):
        while True:
            self.get_STA
            self.get_AP
            for k in sorted(self.completeDict):
                print("{} = {}|".format(k, self.completeDict[k]), end="\t")
            print("", end="\n")
            await asyncio.sleep(5)

    def set_localtime(self):
        # localtime      year,month,day,hour,minute,second,weekday, yearday
        n = self.ds.datetime()
        # datetime ds    year,month,day,weekday,hour,min,second,subsecond
        utime.localtime(utime.mktime(
            (n[0], n[1], n[2], n[4], n[5], n[6], 0, 0)))

    def pumpPinInterrupt(self, Pin):
        print("Pumpenstatus ändern Interrupt")
        self.pumpenstatus = Steuersetup.pumpeANAUS(Pin, self.pumpenrelay)
        utime.sleep(0.3)

    def anzeigeInterrupt(self, Pin):
        print("Nächste Anzeige Interupt")
        if self.screenfeld < len(self.screenfelder):
            self.screenfeld += 1
        else:
            self.screenfeld = 1
        utime.sleep(0.1)

    async def collectGarbage(self):
        while True:
            gc.collect()
            print("Soviele  Bytes sind noch frei: {}".format(gc.mem_free()))
            await asyncio.sleep(15)

    async def readSensoren(self):
        while True:
            temp, hum = Datenlesen.read_DHT_data(self.dht11)
            self.datenDict.update({"temp": temp, "hum": hum})

            tBMP, press = Datenlesen.read_BMP_Data(self.bmp180)
            if tBMP == "--":
                self.start_BMP()
            self.datenDict.update({"tBMP": tBMP, "press": press})
            await asyncio.sleep(2)

    async def updateScreen(self):
        while True:
            try:
                self.oled.fill(0)
                if self.screenfeld == 1:
                    Oledanzeige.showValues(self.oled, self.datenDict)
                elif self.screenfeld == 2:
                    Oledanzeige.showWaage(self.board)
                elif self.screenfeld == 3:
                    Oledanzeige.showIP(self.oled,  self.completeDict,"STA")
                elif self.screenfeld == 4:
                    Oledanzeige.showIP(self.oled,  self.completeDict,"AP")
                self.oled.text("Seite: {}".format(self.screenfeld), 0, 56, 1)
                self.oled.show()

            except Exception as e:
                self.start_OLED()
            await asyncio.sleep_ms(400)
