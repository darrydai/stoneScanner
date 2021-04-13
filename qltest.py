import brother_ql
from brother_ql.raster import BrotherQLRaster
from brother_ql.backends.helpers import send

def sendToPrinter(path):
    # Using USB connected printer 
    PRINTER_IDENTIFIER = '/dev/usb/lp0'
    printer = BrotherQLRaster('QL-800')
    filename = path
    print_data = brother_ql.brother_ql_create.convert(printer, [filename], '62', dither=True,red=False)
    send(print_data, PRINTER_IDENTIFIER)

#sendToPrinter('/home/pi/stoneScanner/data/pic/stamp/stamp_result/stamp_245.png')