import time
from PIL import Image
from pydust import core
import io


# def readPGM():
#    with open('resources/TestL2.png', 'rb') as f:
#        data = bytearray(f.read())
#    return data

def convertPngToBytes():
    img = Image.open('data/map/layer 2/mapLayer2.png', mode='r')

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')

    return img_byte_arr.getvalue()


def main():
    while True:
        # time.sleep(180)
        L2 = convertPngToBytes()
        # initialises the core with the given block name and the directory where the modules are located (default "./modules")
        dust = core.Core("publish-block", "./modules")
        # start a background thread responsible for tasks that shouls always be running in the same thread
        dust.cycle_forever()
        # load the core, this includes reading the libraries in the modules directory to check addons and transports are available
        dust.setup()
        # set the path to the configuration file
        dust.set_configuration_file("configurationMQTT.json")
        # connects all channels
        dust.connect()
        time.sleep(1)
        dust.publish("pub-map-layer-2", bytes(L2))
        time.sleep(1)
        # disconnects all channels and flushes the addon stack and transport.
        dust.disconnect()

        # stops the background thread started by cycleForever() and wait until the thread has finished its tasks before exiting the application
        dust.cycle_stop()


if __name__ == "__main__":
    main()
