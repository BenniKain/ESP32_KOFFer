erstellen von firmware
In Ordner
\\wsl$\Ubuntu\home\benjamin\esp\micropython\ports\esp32 
command : make clean 

\\wsl$\Ubuntu\home\benjamin\esp\micropython\ports\esp32 
command: make



unter folgendem namen ist die firmware zu finden
\\wsl$\Ubuntu\home\benjamin\esp\micropython\ports\esp32\build-GENERIC\firmware.bin 
vermutlich falsch

in folgenden ordner die library files für bytecode reinkopieren
\\wsl$\Ubuntu\home\benjamin\esp\micropython\ports\esp32\modules
man kan auch ordner reinkopieren

bei windows wsl eingeben zum öffnen
in wsl den derzeitigen explorer in windows öffnen
explorer.exe .

	
erase flash on esp; com7 ist der port der harware USB
py -m esptool -p com3 -c esp32 -b 460800 erase_flash 

installiert/flashes bin
py -m esptool -p com3 -c esp32 -b 460800 write_flash --flash_size=detect 0x1000  C:\Users\kainb\OneDrive\Documents\Programmieren\micropython\firmware.bin

