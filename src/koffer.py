from .steuerung.hostserver import app as hostserver
from .steuerung.hostserver import POST_Method as PM
from .libraries.wifi_manager import  WifiManager
from .steuerung.methoden import Steuersetup,Ventilqueue
import uasyncio as asyncio
import uos as os
import network

class App():
    def get_Board (self):
        # checks type of esp and therefore gets the right onstance of the board
        self.boardname = os.uname().sysname
        if  self.boardname == "esp32":
            from .steuerung.boards.esp32 import ESP_32 as ESP
            
        elif self.boardname == "esp8266":
            from .steuerung.boards.esp8266 import ESP8266 as ESP
        return ESP(self.boardname)

    def __init__(self) -> None:
        self.board = self.get_Board()
        self.vq = Ventilqueue(self.board)
        self.wifimngr = WifiManager()
        self.board.set_time()
        self.vq.postmethod = PM()


    def run(self) -> None:
        
        try:
            loop = asyncio.get_event_loop()

            loop.create_task(self.wifimngr.manage())
            loop.create_task(self.board.collectGarbage())
            self.vq.add(self.board.ventil1,dauer=10)# sollte über eine html from ausgeführt werden TODO
            # loop.create_task(self.vq.hinzufügen(self.board.ventil1)) #used for testing the queue
            loop.create_task(self.board.queueing(self.vq))
            self.vq.add(self.board.ventil2,dauer =15)
            loop.create_task(self.vq.newData())
            loop.create_task(self.board.collectGarbage())
            loop.create_task(self.board.readSensoren()) 
            loop.create_task(self.board.updateScreen())
            loop.create_task(self.board.updateIPs())
            loop.create_task(hostserver.run(host=network.WLAN(network.STA_IF).ifconfig()[0]))

            print("Tasks created .. starting event loop ...")
            loop.run_forever()
        except KeyboardInterrupt as e:
            print("KeyboardInterrupt: ",e)
            hostserver.shutdown()
            loop.close()
        except Exception as e:
            raise e# from machine import reset as r
            # import utime
            # print("ERROR {} \nReseting in 5 sec ...".format(e))
            # utime.sleep(5)
            # r()
