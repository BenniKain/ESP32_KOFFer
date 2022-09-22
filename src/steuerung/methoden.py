from time import sleep
import utime
import uasyncio as asyncio
from machine import Pin

class Relay ():
    def an(self):
        return self.r.off()

    def aus(self):
        return self.r.on()
    
    def value (self):
        return not self.r.value()

    def __init__(self,*args,**kwargs) -> None:
        self.r = Pin(*args, mode=Pin.OUT, ** kwargs)
    
class Ventilqueue():
    l = []

    def add (self, ventil, dauer = 30):
        self.l.append((ventil, dauer))

    async def hinzufügen (self,ventil,dauer=3):
        while True:
            self.l.append((ventil, dauer))
            await asyncio.sleep(10)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.l


class Steuersetup():

    def sdcard(self):
        pass
   
        #sd card slot if needed not planned
        #inits SD Card holder
        #https://github.com/micropython/micropython/blob/a1bc32d8a8fbb09bc04c2ca07b10475f7ddde8c3/drivers/sdcard/sdcard.py    
        #spisd = SoftSPI(-1, miso=Pin(12), mosi=Pin(13), sck=Pin(14))
        #sd = SDCard(spisd, Pin(15))
        #print('Root directory:{}'.format(os.listdir()))
        #print(gc.mem_free()) 
        #vfs = os.VfsFat(sd)        #zu wenig speicher um sd karte zu unterstüzen flo fragen
        #os.mount(vfs, '/sd')
        #os.chdir('sd')
        #print('SD Card contains:{}'.format(os.listdir()))
        

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
    async def showIP(self):
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
    def showWaage(self, oled, hx711):
        oled.text('Waagen anzeige:', 0, 0, 1)
        oled.text('Gewicht g: :', 0, 14, 1)
        # len is 4 trotz . wegen float daher 10 sign lang
        oled.text(str(hx711.read()), 128-len(str(hx711.read()))*10, 14, 1)
        oled.text("Tare auf ", 0, 28, 1)
        oled.text(str(hx711.read()), 128 -
                  len(str(round(hx711.offset, 1)))*10, 28, 1)
        print(hx711.read())

    def showValues(self, oled, datenDict):
        oled.text('T C:', 0, 0, 1)
        oled.text(datenDict["temp"], 128-len(datenDict["temp"])*9, 0, 1)
        oled.text('Feuchte %:', 0, 14, 1)
        oled.text(datenDict["hum"], 128-len(datenDict["hum"])*9, 14, 1)
        oled.text('Druck hPa:'.format(datenDict["press"]), 0, 28, 1)
        oled.text(datenDict["press"], 128-len(datenDict["press"])*9, 28, 1)
        oled.text('T C:', 0, 42, 1)
        oled.text(datenDict["tBMP"], 128-len(datenDict["tBMP"])*9, 42, 1)

    def showIP(self, oled, datenDict):
        oled.text('Name:', 0, 0, 1)
        oled.text(datenDict["name"], 128-len(datenDict["name"])*9, 0, 1)
        oled.text('IP:', 0, 14, 1)
        oled.text(datenDict["ip"], 128-len(datenDict["ip"])*9, 14, 1)

    def nextANzeige(self, screenfeld, screenfelder):
        if screenfeld == len(screenfelder):
            screenfeld = 1
        else:
            screenfeld += 1
        sleep(0.1)
        print("anzeige: {}".format(screenfeld))
        return screenfeld


class Datenlesen ():
    @classmethod
    def read_DHT_data(cls,dht11):
        try:
            dht11.measure()
            temp = str(dht11.temperature())
            hum = str(dht11.humidity())
        except Exception as e:
            temp = "--"
            hum = "--"
            print(e)
        finally:
            return temp, hum

    @classmethod
    def read_BMP_Data(cls,bmp180):
        try:
            tBMP = str(round(bmp180.temperature, 1))
            press = str(int(bmp180.pressure / 100))  # in Pa, mit /100 in hPa
            alt = str(round(bmp180.altitude / 100, 0))
            return tBMP, press, alt
        except Exception as e:
            return e
 

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

    def get_htmlfile(self,f):
        myfile = open(f, "r")
        self.htmlstring = ""
        for line in myfile.readlines():
            self.htmlstring += line
        #print (self.htmlstring, " !")
        myfile.close()

    def build_table(self,tabelle):
        if tabelle == "Anzeige":
            from src.koffer import App as Koffer
            
            #    TODO: feting the instance of Koffer from main or src.koffer umboard zu bekommen
        
            #table = self.HTML_tab_bauen("ee")
            table = "ee"
        else:
            table ="Placeholder"

        return table

    def HTML_tab_bauen(self,reihen):
        table = "<table>"
        for k, v in reihen:
            table += "<tr><td>{}</td><td>{}</td></tr>".format(k,v)
        table += "</table>"
        return table
        
    def get_kwargs(self,**kwargs):
        return self.htmlstring.format(**kwargs)
        #eturn ",".join([self.htmlstring.format(v) for k, v in kwargs.items()])

if __name__ == "__main__":
    h = HTML_response("src/html_css/base.html", table="tabelle",
                  command="Kommando", wasaimmerr="nic")
    print(h.response)



