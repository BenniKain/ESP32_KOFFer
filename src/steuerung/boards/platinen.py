from machine import freq,Pin,I2C
import machine,utime,network
from dht import DHT11
from src.libraries import *
from src.steuerung.methoden import Datenlesen,Steuersetup,Oledanzeige
import uasyncio as asyncio
import gc

class Board():
    freq = freq(160000000)    # setzt die frequenz der maschine auf den wert für hx711 waage laut beschreibung
    esp_config_file = "espconfig.json"
    datenDict = {"temp": "--", "hum": "--",
                 "tBMP": "--", "press": "--", "alt": "--"}
    logfile = "/loggingdata/loggingfiles.txt"
    kofferDict = {}
    screenfeld = 1  # für bildschirme zum iterieren von anzeigen
    screenfelder = [i for i in range(1,4)]

    def __init__(self, boardname) -> None:
        config = self.get_config(boardname)
        cPins = config["Pins"]
        print (cPins)
        self.i2c = I2C(scl=Pin(cPins["I2C_scl"]),
                       sda=Pin(cPins["I2C_sda"]), freq=400000)
        self.pumpenrelay = Pin(cPins["pumpenrelay"], Pin.OUT)
        self.pumpentaster = Pin(cPins["pumpentaster"], Pin.IN)
        self.waagen_taster = Pin(cPins["waagentaste"], Pin.IN) 
        #self.hx711 = HX711(pd_sck=cPins["hx711_sck"], dout=cPins["hx711_dout"])
        self.dht11 = DHT11(Pin(cPins["dht11"]))  # inits DHT sensor
        self.anzeigeschalter = Pin(cPins["anzeigeschalter"], Pin.IN)
        
    def get_config(self, boardname):
        import ujson as json
        config_file = "src/steuerung/boardConfs.json"
        with open(config_file, "r") as jsonfile:
            data = json.loads(jsonfile.read())
        return data[boardname]

    def start_BMP(self):
        try:
            self.bmp180 = BMP180(self.i2c)
            print("BMP180 gestartet")
            return True
        except:
            print("BMP180 nicht gestartet")
            return False

    @property
    def get_STA(self):
        if network.WLAN(network.STA_IF).active():
            STA_IP = network.WLAN(network.STA_IF).ifconfig()[0]  # ip ist verbundene sta
            STA_Name = network.WLAN(network.STA_IF).config("essid")
        else:
            STA_IP, STA_Name = "--", "--"

        self.datenDict.update({"STA_IP": STA_IP, "STA_Name": STA_Name})
        return STA_IP,STA_Name
    
    @property
    def get_AP(self):
        if network.WLAN(network.AP_IF).active():
            AP_IP = network.WLAN(network.AP_IF).ifconfig()[0]  # ip ist accesspoint
            AP_Name = network.WLAN(network.AP_IF).config("essid")
        else:
            AP_IP, AP_Name = "--", "--"

        self.datenDict.update({"AP_IP": AP_IP, "AP_Name":AP_Name})
        return AP_IP,AP_Name

    async def updateIPs(self):
        while True:
            self.get_STA
            self.get_AP
            print(self.datenDict)
            await asyncio.sleep(5)

    def set_ds1306Time(self):
        try:
            zeit = Steuersetup.set_ds1306Time()
            # datetime ds    year,month,day,weekday,hour,min,second,subsecond
            self.ds.datetime(zeit)
        except:
            pass

    def set_localtime(self):
        n = self.ds.datetime()  # localtime      year,month,day,hour,minute,second,weekday, yearday
        # datetime ds    year,month,day,weekday,hour,min,second,subsecond
        utime.localtime(utime.mktime(
            (n[0], n[1], n[2], n[4], n[5], n[6], 0, 0)))

    def pumpPinInterrupt(self, Pin):
        print("Pumpenstatus ändern Interrupt")
        self.pumpenstatus = Steuersetup.pumpeANAUS(Pin, self.pumpenrelay)
        utime.sleep(0.3)

    def anzeigeInterrupt(self, Pin):
        print("Nächste Anzeige Interupt")
        self.screenfeld = Oledanzeige.nextANzeige(
            self.screenfeld, self.screenfelder)

    def waagentarInterrupt(self, Pin):
        print("Tare")
        self.hx711.tare()

    async def collectGarbage(self):
        while True:
            gc.collect()
            await asyncio.sleep(15)

    async def readDHT(self):
        while True:
            try:
                temp, hum = Datenlesen.read_DHT_data(self.dht11)    
            except:
                temp,hum = "--","--"
            self.datenDict.update({"temp": temp, "hum": hum})
            print("DHT-Daten upgedated: Temp = {}; Hum = {} ".format(temp,hum))
            await asyncio.sleep(5)
            
    async def readBMP(self):
        while True:
                try:
                    print("Trying to update BMP")
                    tBMP, press, alt = Datenlesen.read_BMP_Data(self.bmp180)
                    print("BMP-Daten upgedated")                
                
                except Exception as e:
                    if self.start_BMP():
                        tBMP, press, alt = Datenlesen.read_BMP_Data(
                            self.bmp180)
                    else:tBMP, press, alt = "--", "--", "--"
                    print ("Error when reading BMP Sensor ",e)
                finally:
                    self.datenDict.update({"tBMP": tBMP, "alt": alt, "press": press})
                    await asyncio.sleep(5)

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
            except:
                pass
            await asyncio.sleep_ms(200)