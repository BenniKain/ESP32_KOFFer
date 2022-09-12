from steuerung.hostserver import app as hostserver
from steuerung.boards.esp32 import ESP32
from micropython_wifimanager.wifi_manager import  WifiManager
import uasyncio as asyncio

wifimngr = WifiManager()
board = ESP32()

class App():
    def __init__(self) -> None:
        loop = asyncio.get_event_loop()

        loop.create_task(wifimngr.manage())

        loop.create_task(board.readBMP())
        loop.create_task(board.readDHT())
        loop.create_task(board.updateScreen())

        loop.create_task(hostserver.run())

        print("Tasks created .. starting event loop ...")
        loop.run_forever()