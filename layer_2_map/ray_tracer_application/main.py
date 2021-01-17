import subscriber
import data_processing
import raytracer
import publisher
from multiprocessing import Process

if __name__ == '__main__':
    # receive all the needed data over MQTT

    proc1 = Process(target=subscriber.main, args=("subscribe-mqtt-map",))
    proc2 = Process(target=subscriber.main, args=("subscribe-mqtt-positional-data",))
    proc3 = Process(target=subscriber.main, args=("subscribe-mqtt-camera-data",))
    proc4= Process(target=data_processing.main)
    proc5 = Process(target=raytracer.main)
    proc6 = Process(target=publisher.main)

    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()
    proc5.start()
    proc6.start()
