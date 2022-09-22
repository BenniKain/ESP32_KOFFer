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
        
        self.ventil1 = Relay(self.cPins["ventil1"])
        self.ventil2 = Relay(self.cPins["ventil2"])
        self.ventil3 = Relay(self.cPins["ventil3"])
        self.ventile = [self.ventil1, self.ventil2, self.ventil3]
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

    async def queueing (self,vq):
        while True:
            self.pumpenrelay.an()
            while vq.l:
                print(vq.l)
                vent,dauer = vq.l.pop(0)
                print("Printing: ",type(vent),dauer)
                vent.an()
                await asyncio.sleep(dauer)
                vent.aus()
            print("No more measuerements in queue")
            self.pumpenrelay.aus()
            await asyncio.sleep(2)
   
            

    async def ventilTest (self,vq):
        self.pumpenrelay.an()
        self.ventil1.aus()
        self.ventil2.aus()
        self.ventil3.aus()
        while True:
            print("Starte ventiltest: Ventil 1 ist ", self.ventil1.value())
            
            try:
                
                if  self.ventil1.value():
                    print ("ventil2 on")
                    self.ventil1.aus()
                    self.ventil2.an()
                    self.ventil3.aus()
                elif  self.ventil2.value():
                    print("ventil3 on")
                    self.ventil1.aus()
                    self.ventil2.aus()
                    self.ventil3.an()
                    #self.pumpenrelay.aus()
                elif  self.ventil3.value():
                    print("ventil1 on")
                    self.ventil1.an()
                    self.ventil2.aus()
                    self.ventil3.aus()
                else:
                    self.ventil1.an()
            except Exception as e:
                print (e)
            await asyncio.sleep(5)