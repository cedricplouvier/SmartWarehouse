import python_proto.ActionMessage_pb2 as ActionMessage
import python_proto.StatusMessage_pb2 as Status
import python_proto.DataStreamMessage_pb2 as DataStream
import python_proto.DecodingProto as DecodingProto
from google.protobuf import any_pb2
from google.protobuf import timestamp_pb2

import CodingProto
import io
from PIL import Image

def test_status():
    msg_main = Status.Main()
    msg = Status.Status()
    msg.id_receiver = 50
    msg.id_command = 10
    msg.id_robot = 5
    msg.status = Status.ActionStatus.Value("ACTIVE")

    msg_main.status.CopyFrom(msg)
    print(msg_main)
    decoded_msg = DecodingProto.parse_status(msg_main.SerializeToString(), 50)

    print(decoded_msg)

    msg = Status.Odometry()
    msg.id_robot = 50
    msg_main.odometry.CopyFrom(msg)

    decoded_msg = DecodingProto.parse_status(msg_main.SerializeToString(), 50)
    print(decoded_msg)

def test_action():
    msg = ActionMessage.ActionMessage()
    msg.id_sender = 50
    msg.id_command = 10
    msg.id_robot = 5

    action = ActionMessage.MoveLocation()
    action.status = ActionMessage.MoveLocation.Status.Value("PAUSE")
    action.size = 2
    action.locations = bytes([0,1,2,3])

    _tmp_action = any_pb2.Any()
    _tmp_action.Pack(action)
    msg.action.CopyFrom(_tmp_action)
    decoded_msg = DecodingProto.parse_action(msg.SerializeToString(), 5)

    print(decoded_msg)

def test_stream():
    # msg = DataStream.Datastream()
    # msg.id_robot = 5

    # datastream = DataStream.GMap()
    # Image.open("bettermap.pgm").convert('1').save("convertedBMP.bmp")
    # im = Image.open("convertedBMP.bmp")
    # im_bytes = io.BytesIO()

    # im.save(im_bytes, format('BMP'))

    # datastream.data = im_bytes.getvalue()

    # _tmp_datastream = any_pb2.Any()
    # _tmp_datastream.Pack(datastream)
    # msg.datastream.CopyFrom(_tmp_datastream)

    # decoded_msg = DecodingProto.parse_stream(msg.SerializeToString())

    # rec_im = Image.open(decoded_msg[2])

    # rec_im.save('receivedBPM.bmp')

    # image_dict = {
    #     'seq': 13164,
    #     'seconds': 1610371862,
    #     'nanoseconds': 110471487,
    #     'frame': '"camera_color_optical_frame"',
    #     'data': [0,0,0,0],
    #     'height': 480,
    #     'width': 640,
    #     "encoding": "rgb8",
    #     "step": 1920,
    #     "endian": 0
    # }

    # msg = CodingProto.serialize_image(50, image_dict)
    # import json
    # file1 = open("image", 'wb')
    # file1.write(msg)
    # file1.close()

    # file2 = open("image.txt", 'rb')
    # msg = file2.read()


    # decoded = DecodingProto.parse_stream(msg)

    # print(decoded)
    

    msg = DataStream.Datastream()
    msg.id_robot = 5

    image_msg = DataStream.Image()
    im_header = DataStream.Image.Header()
    tm_st = timestamp_pb2.Timestamp()
    tm_st.GetCurrentTime()
    im_header.timestamp.CopyFrom(tm_st)

    image_msg.header.CopyFrom(im_header)

    _tm_dat = any_pb2.Any()
    _tm_dat.Pack(image_msg)
    msg.datastream.CopyFrom(_tm_dat)

    decoded_msg = DecodingProto.parse_stream(msg.SerializeToString())

    print(decoded_msg)


def test_serialize():
    ans = CodingProto.serialize_gmap(50,10,20,"bettermap.pgm")
    print(ans)

def test_action_pars():
    ans = CodingProto.serialize_action_location(50,50,50,1,[{'x':5,'y':5,'z':6},{'x':5,'y':5,'z':6}])
    print(ans)
    decoded_ans = DecodingProto.parse_action(ans,50)
    x = decoded_ans[1]['locations']
    print(x)

def test_arm_all():
    ans = CodingProto.serialize_action_arm(10,10,50,{'x':1,'y':2,'z':3,'b':4,'h':5, 'l':6}, "HOLD")
    print(ans)
    dec_and = DecodingProto.parse_action(ans,50)
    print(dec_and)

def test_keep_alive():
    ans = CodingProto.serialize_keepalive(50,'ROBOT')
    print(ans)
    decoded = DecodingProto.parse_alive(ans)
    print(decoded)

if __name__ == "__main__":
    # test_status()
    # test_action()
    # test_stream()
    # test_serialize()
    # test_action_pars()
    # test_arm_all()
    test_keep_alive()
