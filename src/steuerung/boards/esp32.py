from src.steuerung.boards.platinen import Board
from machine import I2C, Pin, reset, SPI,unique_id
from dht import DHT11
from hx711 import HX711
from bmp180 import BMP180
from ssd1306 import SSD1306_I2C
from dht import DHT11
import uasyncio as asyncio
import utime
import network
from src.steuerung.methoden import Relay

class ESP_32 (Board):
    def __init__(self,) -> None:
        boardname = "esp32"
        super().__init__(boardname)      
        
        self.ventil2 = Relay(self.configPins["ventil2"], name="Ventil2")
        self.ventil3 = Relay(self.configPins["ventil3"], name="Ventil3")
        self.ventil1 = Relay(self.configPins["ventil1"], name="Ventil1")
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
        self.completeDict.update({"espID": espID})
        #print("ID des ESP's: ", espID)
        return espID

    async def queueing (self,vq):
        while True:
            try:
                while vq.board.ventilqueueList:
                    self.pumpenrelay.an()
                    par, ventil, dauer, startzeit = vq.board.ventilqueueList[0]
                    for vent in self.ventile:
                        if vent.__name__() == ventil:
                            ventil = vent
    
                    print("Starte Messung des Parameter{} am {} für die nächsten {} min.".format(par, ventil, dauer))
                    ventil.an()
                    
                    await asyncio.sleep(dauer*60)
                    ventil.aus()
                    vq.board.ventilqueueList.pop(0)

                #print("No more measuerements in queue")
                self.pumpenrelay.aus()
            except Exception as e:
                
                print("Fehler in queueing; ",e)
            await asyncio.sleep(.1)  