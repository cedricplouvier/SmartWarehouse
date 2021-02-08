import time
import python_proto.DecodingProto as DecodingProto
from pydust import core
import json
from PIL import Image

# positional data variables
positional_id_robot = 0
positional_timestamp = 0
positional_position = (0, 0)
positional_rotation = (0, 0, 0, 0)
positional_data = {}
positional_data['id_robot'] = []
positional_data['timestamp'] = []
positional_data['position'] = []
positional_data['rotation'] = []

positional_counter = 0
camera_counter = 0
map_counter = 0


def receive_positional_data(arg):
    global positional_counter
    print("Received payload with %d bytes" % len(arg))
    time.sleep(2)
    data = arg.decode()

    with open('data/positional data/positional_data_{}.json'.format(positional_counter), 'w') as outfile:
        outfile.write(data)
    with open('data/odometry/positional_data_{}.json'.format(positional_counter), 'w') as outfile:
        outfile.write(data)

    positional_counter += 1


def main(channel):
    # initialises the core with the given block name and the directory where the modules are located (default
    # "./modules")
    dust = core.Core("subscribe-block", "./modules")
    # start a background thread responsible for tasks that shouls always be running in the same thread
    dust.cycle_forever()
    # load the core, this includes reading the libraries in the modules directory to check addons and transports are
    # available
    dust.setup()
    # set the path to the configuration file
    dust.set_configuration_file("configurationMQTT.json")
    # connects all channels
    dust.connect()
    # add a message listener on the subscribe-tcp channel. The callback function takes a bytes-like object as
    # argument containing the payload of the message
    # TODO: check channels
    if channel == "subscribe-mqtt-positional-data":
        dust.register_listener("subscribe-mqtt-positional-data", receive_positional_data)
    else:
        print("Channel not defined.")
    while True:
        # print("waiting for data on channel {}.".format(channel))
        time.sleep(1)
