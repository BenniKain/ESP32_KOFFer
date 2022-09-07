from machine import freq
import machine,utime,network
from methoden import Datenlesen,Steuersetup,Oledanzeige
from uasyncio import asyncio

class Board():
    freq = freq(160000000)    # setzt die frequenz der maschine auf den wert für hx711 waage laut beschreibung
    esp_config_file = "espconfig.json"
    datenDict = {"temp": "--", "hum": "--",
                 "tBMP": "--", "press": "--", "alt": "--"}
    logfile = "/loggingdata/loggingfiles.txt"
    kofferDict = {}
    screenfeld = 1  # für bildschirme zum iterieren von anzeigen
    screenfelder = [i for i in range(1,4)]


    def __init__(self) -> None:
        pass

    def get_IP(self):
        essid = network.WLAN(network.STA_IF).config("essid")
        if essid == "Emi-Koffer":
            ip = network.WLAN(network.STA_IF).ifconfig()[
                0]  # ip ist verbundene sta
        elif essid != "Emi-Koffer":
            ip = network.WLAN(network.AP_IF).ifconfig()[
                0]  # ip ist accesspoint
        self.datenDict.update({"ip": ip})
        return ip

    def get_espID(self):
        import esp
        espID = str(esp.flash_id())
        self.datenDict.update({"espID": espID})
        print("ID des ESP's: ", espID)
        return espID

    def update_Kofferdict(self, dataDict):
        self.kofferDict.update({dataDict["espID"]: dataDict})

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

    async def readData(self):
        while True:
            try:
                temp, hum = Datenlesen.read_DHT_data(self.dht11)
                self.datenDict.update({"temp": temp, "hum": hum})
                if self.bmpYN:
                    tBMP, press, alt = Datenlesen.read_BMP_Data(self.bmp180)
                    self.datenDict.update(
                        {"tBMP": tBMP, "alt": alt, "press": press})
            except Exception as e:
                print("Fehler bei ReadData Methode: ", e)
                #raise e
            finally:
                print("Daten upgedated: ", self.datenDict)
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

