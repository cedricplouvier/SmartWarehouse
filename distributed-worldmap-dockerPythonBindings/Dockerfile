FROM ubuntu:18.04

#Install python
RUN apt update && apt -y install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt -y install python3.7

RUN apt-get update && \
    apt-get -y install cmake build-essential gcc-7 g++-7 && \
    apt-get -y install rapidjson-dev libmosquitto-dev && \
    apt-get -y install libboost-python-dev && \
    apt-get -y install libsodium-dev && \
    apt-get -y install libkrb5-dev && \
    apt-get -y install libsodium23 && \
    apt-get -y install python3-setuptools   

# Install Dust
WORKDIR /usr/src
copy dust-core dust-core
WORKDIR /usr/src/dust-core/build
RUN cmake .. -DWITH_EXAMPLES=ON && make && make install
RUN cd .. && rm -rf build/

# Install dependencies for modules
WORKDIR /usr/src
copy lib lib
WORKDIR /usr/src/lib/libzmq/build
RUN cmake .. && make -j4 install
WORKDIR /usr/src/lib/cppzmq/build
RUN cmake -DCPPZMQ_BUILD_TESTS=OFF .. && make -j4 install
WORKDIR /usr/src
RUN rm -rfd lib

#Install ZMQ module
WORKDIR /usr/src
Copy zmq-module zmq-module
WORKDIR /usr/src/zmq-module/build
RUN cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4


#Install MQTT module
WORKDIR /usr/src
Copy mqtt-module mqtt-module
WORKDIR /usr/src/mqtt-module/build
RUN cmake -DCMAKE_BUILD_TYPE=RELEASE .. && make -j4


#Install python bindings
WORKDIR /usr/src
COPY dust-2-python dust-2-python
WORKDIR /usr/src/dust-2-python
RUN python3 setup.py build && python3 setup.py install

RUN ldconfig


