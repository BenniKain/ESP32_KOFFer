# boot.py -- run on boot-up

import gc
import network

gc.enable()

sta = network.WLAN(network.STA_IF)
sta.active(True)
try:
    import ntptime
    ntptime.settime()  # set the rtc datetime from the remote server geht eine stunde falsch wegen zeitverschiebung. rtc.dattime nimmt komisches argument, nicht geschafft
    print("System-Uhrzeit eingestellt")
except:
    pass

sta.connect("HUAWEI-40EE", "55275248")

print("Station IP:    \t{}".format(sta.ifconfig()[0]))
print("Station ESSID:    \t{}".format(sta.config("essid")))
