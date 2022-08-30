import uasyncio as asyncio
import src.steuerung
import src.libraries
import dht

hostserver = src.steuerung.hostserver

def start_tasks():
    loop = asyncio.get_event_loop()
    loop.create_task(hostserver.run())
    print("Tasks created .. starting event loop ...")
    loop.run_forever()

print("Alles erfolgreich")
#start_tasks() #started die Eventloops


