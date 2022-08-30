from src.libraries.ST7735.ST7735 import TFT
from src.libraries.ST7735.sysfont import sysfont
from machine import SPI, Pin
import time
import math

class Test():
    def __init__(self) -> None:
        self.spi = SPI(2, baudrate=20000000, polarity=0, phase=0,
        sck=Pin(14), mosi=Pin(13), miso=Pin(12))
        self.tft = TFT(self.spi, 16, 17, 18)
        self.tft.initr()
        self.tft.rgb(True)

    def testlines(self,color):
        self.tft.fill(TFT.BLACK)
        for x in range(0, tft.size()[0], 6):
            self.tft.line((0,0),(x, tft.size()[1] - 1), color)
        for y in range(0, tft.size()[1], 6):
            self.tft.line((0,0),(tft.size()[0] - 1, y), color)

    def test_main(self):
        self.tft.fill(TFT.GREEN)
        #tft.text((0, 0), "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur adipiscing ante sed nibh tincidunt feugiat. Maecenas enim massa, fringilla sed malesuada et, malesuada sit amet turpis. Sed porttitor neque ut ante pretium vitae malesuada nunc bibendum. Nullam aliquet ultrices massa eu hendrerit. Ut sed nisi lorem. In vestibulum purus a tortor imperdiet posuere. ", TFT.WHITE, sysfont, 1)
        
if __name__ == "__main__":
    Test.test_main()