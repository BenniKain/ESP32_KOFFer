from .steuerung.hostserver import app as hostserver
from .libraries.wifi_manager import  WifiManager
from .steuerung.methoden import Steuersetup
import uasyncio as asyncio
import uos as os
import network

class App():
    def get_Board (self):
        # checks type of esp and therefore gets the right onstance of the board
        boardname = os.uname().sysname
        if  boardname== "esp32":
            from .steuerung.boards.esp32 import ESP_32 as ESP
            
        elif boardname == "esp8266":
            from src.steuerung.boards.esp8266 import ESP8266 as ESP
        return ESP(boardname)


    def __init__(self) -> None:
        self.board = self.get_Board()
        wifimngr = WifiManager()
        loop = asyncio.get_event_loop()

        loop.create_task(wifimngr.manage())
        loop.create_task(Steuersetup.showIP())

        loop.create_task(self.board.collectGarbage())
        loop.create_task(self.board.readBMP())
        loop.create_task(self.board.readDHT())   
        loop.create_task(self.board.updateScreen())
        loop.create_task(self.board.updateIPs())
        loop.create_task(hostserver.run(host=network.WLAN(network.STA_IF).ifconfig()[0]))

        print("Tasks created .. starting event loop ...")
        loop.run_forever()