from time import sleep
import utime
class Steuersetup():

    def sdcard(self):
        pass
        """
        #sd card slot if needed not planned
        #inits SD Card holder
        #https://github.com/micropython/micropython/blob/a1bc32d8a8fbb09bc04c2ca07b10475f7ddde8c3/drivers/sdcard/sdcard.py    
        spisd = SoftSPI(-1, miso=Pin(12), mosi=Pin(13), sck=Pin(14))
        sd = SDCard(spisd, Pin(15))
        print('Root directory:{}'.format(os.listdir()))
        print(gc.mem_free()) 
        vfs = os.VfsFat(sd)        #zu wenig speicher um sd karte zu unterstüzen flo fragen
        os.mount(vfs, '/sd')
        os.chdir('sd')
        print('SD Card contains:{}'.format(os.listdir()))
        """

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
    def read_DHT_data(self, dht11):
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

    def read_BMP_Data(self,bmp180):
        try:
            tBMP    =   str(round(bmp180.temperature,1))
            press   =   str(int(bmp180.pressure /100))   #in Pa, mit /100 in hPa
            alt     =   str(round(bmp180.altitude /100,0))
        except Exception as e:
            tBMP,press,alt = "--","--","--"
            print(e)
        finally:
            return tBMP,press,alt
    
    def connect_Wifi(cls, ssid, password) -> bool:
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            wlan.connect(ssid, password)
            for check in range(0, 10):
                if wlan.isconnected():
                    return True
                sleep(0.5)
        except:
            return False
            
    def save_new_Wifi(self, **args):
        # wird nicht wahr trotz handy wlan testeingabe
        if self.connect_Wifi(args["ssid"], args["password"]):
            import json
            config_file = "/networks.json"
            with open(config_file, "r") as f: #liest json und speichert in var
                config = json.loads(f.read())
            #erweitert known networks Dict
            config['known_networks'].append({ 
                "ssid": args["ssid"],
             			"password": args["password"],
             			"enables_webrepl": False})

            with open(config_file, "w")as f:  # speichern der geänderten var als Json datei
                json.dump(config, f)
            print("Netzwerk aufgenommen: ", args["ssid"])
            return "W-Lan verbunden und gespeichert"
        return "Fehler bei verbinden des W-Lans!"
