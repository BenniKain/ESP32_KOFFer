from src.steuerung.boards.platinen import Board
from machine import I2C, Pin, reset, SPI,unique_id
from src.libraries import *
from dht import DHT11
import uasyncio as asyncio
import utime
import network

#from steuerung.methoden import Datenlesen,Steuersetup,Oledanzeige

class ESP_32 (Board):
    def __init__(self, boardname) -> None:
        super().__init__(boardname)      
        
        #ds = DS1307(i2c)
        """
        self.pumpentaster.irq(trigger=Pin.IRQ_FALLING |
                              Pin.IRQ_RISING, handler=self.pumpPinInterrupt)
        self.anzeigeschalter.irq(
            trigger=Pin.IRQ_RISING, handler=self.anzeigeInterrupt)
        self.waagen_taster.irq(trigger=Pin.IRQ_RISING,
                               handler=self.waagentarInterrupt)
        """
        self.get_espID
        
    @property
    def get_espID(self):
        import ubinascii
        espID = str(ubinascii.hexlify(unique_id()).decode("utf-8"))
        self.datenDict.update({"espID": espID})
        print("ID des ESP's: ", espID)
        return espID