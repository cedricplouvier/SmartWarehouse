import subscriber
import raytracer
import publisher

from multiprocessing import Process

if __name__ == '__main__':
    # receive all the needed data over MQTT

    # TODO: change configuration
    proc2 = Process(target=subscriber.main, args=("subscribe-mqtt-positional-data",))
    proc5 = Process(target=raytracer.main)
    proc6 = Process(target=publisher.main)

    proc2.start()
    proc5.start()
    proc6.start()
