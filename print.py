import logging
import configparser
from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster

# init config
config = configparser.ConfigParser()
config.read('/home/pi/stoneScanner/stone_scanner.ini')

backend = config['printer']['backend']  # 'pyusb', 'linux_kernal', 'network'
model = config['printer']['model'] # your printer model.
printer = config['printer']['printer'] 

im = Image.open('/home/pi/stoneScanner/data/pic/stamp/stamp_result/stamp_0.png')  

qlr = BrotherQLRaster(model)
qlr.exception_on_warning = True

instructions = convert(
    qlr=qlr, 
    images=[im],    #  Takes a list of file names or PIL objects.
    label=config['printer']['label'], 
    dither=False, 
    compress=False, 
    red=bool(config['printer']['label']),    # Only True if using Red/Black 62 mm label tape.
    dpi_600=False, 
    lq=False,    # True for low quality.
    no_cut=False
)


printstate = send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)
print(printstate['did_print'],printstate['ready_for_next_job'])