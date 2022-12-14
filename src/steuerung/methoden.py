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

    def __init__(self, board) -> None:
        self.sommerzeit = board.sommerzeit
        self.board = board

    async def newData(self):
        while True:
            while self.postmethod.data:
                req = ((self.postmethod.data.pop(0)))
                self.add(req["ventil"], parameter=req["parameter"],
                         dauer=int(req["dauer"]), startzeit= req["time"])
            # print(self.board.ventilqueueList)
            await asyncio.sleep(.1)

    def set_Startzeit(self, pos):
        if self.sommerzeit:
            summertime = 3600
        else:
            summertime = 0
        zeit, j = 0, 0
        for i in self.board.ventilqueueList:
            if j == pos:
                print("verzögerung ", zeit)
                break
            print(i[2])
            zeit += i[2]
            j += 1

        startzeit = list(utime.localtime(
            utime.mktime(utime.localtime()) + 3600+summertime))
        minute = round((startzeit[4]+zeit) % 60)
        if minute < 10:
            minute = "0{}".format(minute)
        else:
            minute = "{}".format(minute)

        extrastunden = (startzeit[4]+zeit) // 60
        stunde = round((startzeit[3]+extrastunden) % 24)
        return stunde, minute

    def add(self, ventil, dauer=30,parameter ="default",startzeit = ""):
        stunde, minute = self.set_Startzeit(len(self.board.ventilqueueList))
        print("Startzeit {}:{}".format(stunde, minute))
        self.board.ventilqueueList.append([parameter, ventil, dauer,
                      "{}:{}".format(stunde, minute)])

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.board.ventilqueueList


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

class Oledanzeige():
    @classmethod
    def showWaage(cls, board):
        oled = board.oled 
        hx711 = board.hx711
        if board.hx711Active:
                val = hx711.read()
        else:
            try:
                board.start_HX711()
                val = hx711.read()
            except:
                val="Error"

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
    def showIP(cls, oled, completeDict,mode):
        
        oled.text('WiFi Name:', 0, 0, 1)
        oled.text(completeDict["{}_Name".format(mode)], 128 -
                  len(completeDict["{}_Name".format(mode)])*9, 14, 1)
        oled.text('WiFi IP:', 0, 28, 1)
        oled.text(completeDict["{}_IP".format(mode)],
                  128-len(completeDict["{}_IP".format(mode)])*9, 42, 1)


class Datenlesen ():
    @classmethod
    def read_DHT_data(cls, dht11):
        try:
            dht11.measure()
            temp = str(dht11.TcalSteigung *dht11.temperature()+dht11.TcalOffset)
            hum = str(dht11.humcalSteigung *dht11.humidity()+dht11.humcalOffset)
        except Exception as e:
            temp = "--"
            hum = "--"
            print("Failed to read DHT Sensor: ", e)
        finally:
            return temp, hum

    @classmethod
    def read_BMP_Data(cls, bmp180):
        try:
            tBMP = str(round(bmp180.TcalSteigung *bmp180.temperature+bmp180.TcalOffset,1))
            press = str(int(bmp180.pressure *bmp180.pressure()+bmp180.PcalOffset/100))# in Pa, mit /100 in hPa

        except Exception as e:
            print("Failed to read BMP Sensor: ", e)
            tBMP, press, = "--", "--"
        finally:
            return tBMP, press

    def save_new_Wifi(self, **args):
        # wird nicht wahr trotz handy wlan testeingabe
        if self.connect_Wifi(args["ssid"], args["password"]):
            import ujson as json
            config_file = "/src/static/config/networks.json"
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