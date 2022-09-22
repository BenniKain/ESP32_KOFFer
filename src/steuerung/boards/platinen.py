from machine import freq, Pin, I2C
import machine
import utime
import network
from dht import DHT11
from src.libraries import *
from src.steuerung.methoden import Datenlesen, Steuersetup, Oledanzeige, Relay
import uasyncio as asyncio
import gc


class Board():
    
    esp_config_file = "espconfig.json"
    datenDict = {"temp": "--", "hum": "--",
                  "tBMP": "--", "alt": "--", "press": "--",
                  "STA_Name":"--","STA_IP":"--"}
    logfile = "/loggingdata/loggingfiles.txt"
    kofferDict = {}
    screenfeld = 1  # für bildschirme zum iterieren von anzeigen
    screenfelder = [i for i in range(1, 4)]

    def __init__(self, boardname) -> None:
        self.config = self.get_config(boardname)
        self.cPins = self.config["Pins"]
        self.i2c = I2C(scl=Pin(self.cPins["I2C_scl"]),
                       sda=Pin(self.cPins["I2C_sda"]), freq=400000)
        self.pumpenrelay = Relay(self.cPins["pumpenrelay"])
        #self.pumpentaster = Pin(self.cPins["pumpentaster"], Pin.IN)
        self.dht11 = DHT11(Pin(self.cPins["dht11"]))  # inits DHT sensor
        self.get_anzeige()
        self.start_HX711()
        self.start_BMP()
        self.start_OLED()

    def get_config(self, boardname):
        import ujson as json
        config_file = "src/steuerung/boardConfs.json"
        with open(config_file, "r") as jsonfile:
            data = json.loads(jsonfile.read())
        return data[boardname]
    def get_anzeige(self):
        self.anzeigeschalter = Pin(self.cPins["anzeigeschalter"], Pin.IN,Pin.PULL_DOWN)
        self.anzeigeschalter.irq(
            trigger=Pin.IRQ_RISING, handler=self.anzeigeInterrupt)

    def start_HX711(self):
        try:
            # setzt die frequenz der maschine auf den wert für hx711 waage laut beschreibung
            self.freq = freq(160000000)
            self.hx711 = HX711(pd_sck=self.cPins["hx711_sck"], 
                                dout=self.cPins["hx711_dout"])
            self.hx711.SCALING_FACTOR = self.config["Waage"]["SCALING_FACTOR"]
            self.waagenTaste = Pin(
                self.cPins["waagenTaste"], Pin.IN, Pin.PULL_DOWN)
            self.waagenTaste.irq(trigger=Pin.IRQ_RISING,
                                handler=self.waagentarInterrupt)
        except Exception as e:
            print("Starten der HX711 Waage fehlgeschlagen: ",e)
    
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
            print("Error Oled Display: rebooting now...\t", e)

    @property
    def get_STA(self):
        if network.WLAN(network.STA_IF).active():
            STA_IP = network.WLAN(network.STA_IF).ifconfig()[
                0]  # ip ist verbundene sta
            STA_Name = network.WLAN(network.STA_IF).config("essid")
        else:
            STA_IP, STA_Name = "--", "--"

        self.datenDict.update({"STA_IP": STA_IP, "STA_Name": STA_Name})
        return STA_IP, STA_Name

    @property
    def get_AP(self):
        if network.WLAN(network.AP_IF).active():
            AP_IP = network.WLAN(network.AP_IF).ifconfig()[
                0]  # ip ist accesspoint
            AP_Name = network.WLAN(network.AP_IF).config("essid")
        else:
            AP_IP, AP_Name = "--", "--"

        self.datenDict.update({"AP_IP": AP_IP, "AP_Name": AP_Name})
        return AP_IP, AP_Name

    async def updateIPs(self):
        while True:
            self.get_STA
            self.get_AP
            for k in sorted(self.datenDict):
                print("{} = {}|".format(k, self.datenDict[k]), end="\t")
            print("", end="\n")
            await asyncio.sleep(5)

    def set_ds1306Time(self):
        try:
            zeit = Steuersetup.set_ds1306Time()
            # datetime ds    year,month,day,weekday,hour,min,second,subsecond
            self.ds.datetime(zeit)
        except:
            pass

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
            await asyncio.sleep(15)

    async def readSensoren(self):
        while True:
            temp, hum = Datenlesen.read_DHT_data(self.dht11)
            self.datenDict.update({"temp": temp, "hum": hum})

            tBMP, press, alt = Datenlesen.read_BMP_Data(self.bmp180)
            if tBMP == "--":
                self.start_BMP()
            self.datenDict.update({"tBMP": tBMP, "alt": alt, "press": press})
            await asyncio.sleep(2)

    async def updateScreen(self):
        while True:
            try:
                self.oled.fill(0)
                if self.screenfeld == 1:
                    Oledanzeige.showValues(self.oled, self.datenDict)
                elif self.screenfeld == 2:
                    Oledanzeige.showWaage(self.oled, self.hx711)
                elif self.screenfeld == 3:
                    Oledanzeige.showIP(self.oled, self.datenDict)
                self.oled.text("Seite: {}".format(self.screenfeld), 0, 56, 1)
                self.oled.show()

            except Exception as e:
                self.start_OLED()
            await asyncio.sleep_ms(400)