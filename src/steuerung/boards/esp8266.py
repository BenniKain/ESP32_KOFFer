import SSD1306_I2C
from boards import Board
from machine import SoftI2C, Pin, reset, SoftSPI
from libraries import HX711
from libraries import BMP180  # druck und t sensor
from libraries import DS1307
f#rom libraries import SSD1306_I2C
from dht import DHT11
import uasyncio as asyncio
import utime
import network
from steuerung.methoden import Datenlesen, Steuersetup, Oledanzeige

class ESP8266(Board):
    pins = {"D0": 16, "D1": 5, "D2": 4, "D3": 0, "D4": 2,
            "D5": 14, "D6": 12, "D7": 13, "D8": 15, "A0": 0, "TX": 1, "RX": 3}
    i2c = SoftI2C(Pin(pins["D1"]), Pin(pins["D2"]))  # d1 ist scl d2 sca
    # D7 D8 is always pulled down geht nicht D3 und D4 pulled up always
    pumpenrelay = Pin(pins["D7"], Pin.OUT)
    # d8 is pulled up daher muss man mit vcc leiter
    pumpentaster = Pin(pins["D3"], Pin.IN)
    waagen_taster = Pin(pins["D4"], Pin.IN)  # inits waage hx711
    hx711 = HX711(pd_sck=pins["D5"], dout=pins["D6"])
    dht11 = DHT11(Pin(pins["D0"]))  # inits DHT sensor
    anzeigeschalter = Pin(pins["D8"], Pin.IN)

    def __init__(self,boardtype) -> None:
        self.get_config(boardtype)
        try:
            self.bmp180 = BMP180(self.i2c)
            self.bmpYN = True
            print("BMP180 gestartet")
        except:
            self.bmpYN = False
            print("BMP180 nicht gestartet")
        #ds = DS1307(i2c)
        
            reset()

        self.pumpentaster.irq(trigger=Pin.IRQ_FALLING |
                              Pin.IRQ_RISING, handler=self.pumpPinInterrupt)
        self.anzeigeschalter.irq(
            trigger=Pin.IRQ_RISING, handler=self.anzeigeInterrupt)
        self.waagen_taster.irq(trigger=Pin.IRQ_RISING,
                               handler=self.waagentarInterrupt)
        self.get_IP()
        self.get_espID()
