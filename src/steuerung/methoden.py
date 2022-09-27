from time import sleep
import utime
import uasyncio as asyncio
from machine import Pin


class Relay ():
    def an(self):
        return self.r.off()

    def aus(self):
        return self.r.on()

    def value(self):
        return not self.r.value()

    def __init__(self, *args, name="Default_Name", **kwargs) -> None:
        self.name = name
        self.r = Pin(*args, mode=Pin.OUT, ** kwargs)
        self.aus()

    def __name__(self):
        return self.name


class Ventilqueue():
    l = []
    lNames = ["Ventil-Name", "Zeitdauer in min","Startzeit"]
  
    def __init__(self,board) -> None:
        self.sommerzeit = board.sommerzeit

    def set_Startzeit(self,pos):
        if self.sommerzeit:
            summertime = 3600
        else:
            summertime = 0
        zeit,j = 0,0
        for i in self.l:
            if j == pos:
                print("verzögerung ", zeit)
                break
            zeit += i[1]
            j+=1

        
        startzeit = list(utime.localtime(
            utime.mktime(utime.localtime()) + 3600+summertime))
        print(startzeit)
        minute = round((startzeit[4]+zeit) % 60)
        extrastunden = (startzeit[4]+zeit) // 60
        stunde = round((startzeit[3]+extrastunden) % 24)
        return stunde,minute

    def add(self, ventil, dauer=30):
        stunde,minute = self.set_Startzeit(len(self.l))
        print("Startzeit {}:{}".format(stunde,minute))
        self.l.append([ventil.__name__(), dauer,"{}:{}".format(stunde,minute)])

    async def hinzufügen(self, ventil, dauer=30):
        while True:
            self.add((ventil, dauer))
            await asyncio.sleep(dauer)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.l


class Steuersetup():

    def pumpeANAUS(cls, Pin, pumpenrelay):
        print("value of the InterruptPin: ", Pin.value())
        if Pin.value() == 0:
            print("Pumpe An")
            pumpenrelay.on()
            pumpenstatus = False
        elif Pin.value() == 1:
            print("Pumpe Aus")
            pumpenrelay.off()
            pumpenstatus = True
        return pumpenstatus

    def set_ds1306Time(cls):
        try:
            import ntptime
            ntptime.settime()  # settime von server Internet
            # +1 zeitverschiebung    #localtime      year,month,day,hour,minute,second,weekday, yearday
            n = utime.localtime(utime.mktime(utime.localtime()) + 3600)
            # datetime ds    year,month,day,weekday,hour,min,second,subsecond
            return (n[0], n[1], n[2], 0, n[3], n[4], n[5], 0)
        except:
            pass

    @classmethod
    async def showIP(cls):
        import network
        ap = network.WLAN(network.AP_IF)
        sta = network.WLAN(network.STA_IF)
        while True:
            print("Accespoint IP {} \t NAme: {}".format(
                ap.ifconfig()[0], ap.config("essid")))
            print("Stationpint IP {} \t NAme: {}".format(
                sta.ifconfig()[0], sta.config("essid")))
            await asyncio.sleep(5)


class Oledanzeige():
    @classmethod
    def showWaage(cls, oled, hx711):
        val = hx711.read()
        oled.text('Waage', 0, 0, 1)
        oled.text("Gewicht in g:", 0, 14)
        # len is 4 trotz . wegen float daher 10 sign lang
        oled.text(str(val), 0, 28, 1)
        print(val)

    @classmethod
    def showValues(cls, oled, datenDict):
        oled.text('T C:', 0, 0, 1)
        oled.text(datenDict["temp"], 128-len(datenDict["temp"])*9, 0, 1)
        oled.text('Feuchte %:', 0, 14, 1)
        oled.text(datenDict["hum"], 128-len(datenDict["hum"])*9, 14, 1)
        oled.text('Druck hPa:'.format(datenDict["press"]), 0, 28, 1)
        oled.text(datenDict["press"], 128-len(datenDict["press"])*9, 28, 1)
        oled.text('T C:', 0, 42, 1)
        oled.text(datenDict["tBMP"], 128-len(datenDict["tBMP"])*9, 42, 1)

    @classmethod
    def showIP(cls, oled, datenDict):
        oled.text('WiFi Name:', 0, 0, 1)
        oled.text(datenDict["STA_Name"], 128 -
                  len(datenDict["STA_Name"])*9, 14, 1)
        oled.text('WiFi IP:', 0, 28, 1)
        oled.text(datenDict["STA_IP"], 128-len(datenDict["STA_IP"])*9, 42, 1)


class Datenlesen ():
    @classmethod
    def read_DHT_data(cls, dht11):
        try:
            dht11.measure()
            temp = str(dht11.temperature())
            hum = str(dht11.humidity())
        except Exception as e:
            temp = "--"
            hum = "--"
            print("Failed to read DHT Sensor: ", e)
        finally:
            return temp, hum

    @classmethod
    def read_BMP_Data(cls, bmp180):
        try:
            tBMP = str(round(bmp180.temperature, 1))
            press = str(int(bmp180.pressure / 100))  # in Pa, mit /100 in hPa
            alt = str(round(bmp180.altitude / 100, 0))

        except Exception as e:
            print("Failed to read BMP Sensor: ", e)
            tBMP, press, alt = "--", "--", "--"
        finally:
            return tBMP, press, alt

    def save_new_Wifi(self, **args):
        # wird nicht wahr trotz handy wlan testeingabe
        if self.connect_Wifi(args["ssid"], args["password"]):
            import json
            config_file = "/networks.json"
            with open(config_file, "r") as f:  # liest json und speichert in var
                config = json.loads(f.read())
            # erweitert known networks Dict
            config['known_networks'].append({
                "ssid": args["ssid"],
                "password": args["password"],
                "enables_webrepl": False})

            with open(config_file, "w")as f:  # speichern der geänderten var als Json datei
                json.dump(config, f)
            print("Netzwerk aufgenommen: ", args["ssid"])
            return "W-Lan verbunden und gespeichert"
        return "Fehler bei verbinden des W-Lans!"


class HTML_response ():
    def __init__(self, f) -> None:
        self.get_htmlfile(f)

    def get_htmlfile(self, f):
        myfile = open(f, "r")
        self.htmlstring = ""
        for line in myfile.readlines():
            self.htmlstring += line
        #print (self.htmlstring, " !")
        myfile.close()

    def build_table(self, tabelle):
        from main import k as koffer
        if tabelle == "Anzeige":
            table = self.create_table(
                koffer.board.datenDict.items(), üsliste=["Name", "Wert"])

        elif tabelle == "Config":
            config = koffer.board.get_config(koffer.boardname)
            dictitems = {}
            for k in config:
                for configKey in config[k]:
                    dictitems[configKey] = config[k][configKey]
            table = self.create_table(
                dictitems.items(), üsliste=["Name", "Wert"])

        elif tabelle == "ESPConfig":
            config = koffer.board.get_ESP_Config()
            dictitems = {}
            for k in config:
                dictitems[k] = config[k]
                
            table = self.create_table(
                dictitems.items(), üsliste=["Name", "Wert"])

        elif tabelle == "Ventilqueue":
            table = self.create_table(koffer.vq.l, üsliste=koffer.vq.lNames)

        else:
            table = "Placeholder"
        return table

    def create_table(self, datendict, üsliste=""):
        table = "<table>"
        table += self.build_tab_überschrift(üsliste)
        for data in datendict:
            print("Data ", data)
            table += "<tr>"
            for row in data:
                table += "<td>{}</td>".format(row)
            table += "</>"
        table += "</table>"
        return table

    def build_tab_überschrift(self, überschriftlist):
        table = "<tr>"
        for i in überschriftlist:
            table += "<th>{}</th>".format(i)
        table += "</tr>"
        return table

    def get_kwargs(self, **kwargs):
        return self.htmlstring.format(**kwargs)

if __name__ == "__main__":
    h = HTML_response("src/html_css/base.html", table="tabelle",
                      command="Kommando", wasaimmerr="nic")
    print(h.response)
