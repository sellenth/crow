from PIL import Image
import qrcode

img=qrcode.make('True')
img.save("test.png")
