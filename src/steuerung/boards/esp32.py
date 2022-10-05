from src.steuerung.boards.platinen import Board
from machine import I2C, Pin, reset, SPI,unique_id
from src.libraries import *
from dht import DHT11
import uasyncio as asyncio
import utime
import network
from src.steuerung.methoden import Relay

#from steuerung.methoden import Datenlesen,Steuersetup,Oledanzeige

class ESP_32 (Board):
    def __init__(self, boardname) -> None:
        super().__init__(boardname)      
        
        self.ventil1 = Relay(self.cPins["ventil1"], name="Ventil1")
        self.ventil2 = Relay(self.cPins["ventil2"], name="Ventil2")
        self.ventil3 = Relay(self.cPins["ventil3"], name="Ventil3")
        self.ventile = [self.ventil1, self.ventil2, self.ventil3]
        #ds = DS1307(i2c)
        """
        self.pumpentaster.irq(trigger=Pin.IRQ_FALLING |
                              Pin.IRQ_RISING, handler=self.pumpPinInterrupt)
        """
        self.get_espID
        
    @property
    def get_espID(self):
        import ubinascii
        espID = str(ubinascii.hexlify(unique_id()).decode("utf-8"))
        self.datenDict.update({"espID": espID})
        #print("ID des ESP's: ", espID)
        return espID

    async def queueing (self,vq):
        while True:
            try:
                
                while vq.l:
                    self.pumpenrelay.an()
                    par,vent,dauer,startzeit = vq.l.pop(0)
                    print("Printing: ",par, vent, dauer)
                    vent.an()
                    await asyncio.sleep(dauer)
                    vent.aus()
                print("No more measuerements in queue")
                self.pumpenrelay.aus()
            except Exception as e:
                print(e)
            await asyncio.sleep(2)
   