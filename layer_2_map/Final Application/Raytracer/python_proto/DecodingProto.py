import python_proto.StatusMessage_pb2 as Status
import python_proto.DataStreamMessage_pb2 as DataStream
import python_proto.ActionMessage_pb2 as Action
import python_proto.KeepAlive_pb2 as KeepAlive
from google.protobuf import any_pb2
from google.protobuf import timestamp_pb2
import io

ActionStatus_dict = {
    0: 'PENDING',
    1: 'ACTIVE',
    2: 'DONE',
    3: 'FAILED',
    4: 'ERROR',
    5: 'ABORTED'
}

MoveLocation_dict = {
    0: 'ABORT',
    1: 'PAUSE',
    2: 'STOP',
    3: 'GO'
}

ArmAction_dict = {
    0: 'PICK',
    1: 'PLACE',
    2: 'HOLD'
}

Alive_dict = {
    0: 'ROBOT',
    1: 'NODE'
}

def parse_status(message, id_receiver):
    msg = Status.Main()
    msg.ParseFromString(message)

    main_type = msg.WhichOneof('main')

    if main_type == "status":
        status_msg = Status.Status()
        status_msg = msg.status

        if id_receiver != status_msg.id_receiver:
            return False
        status_dict = {
            'id_receiver': status_msg.id_receiver,
            'id_command': status_msg.id_command,
            'id_robot': status_msg.id_robot,
            'status': ActionStatus_dict[status_msg.status]
        }
        return "STAT", status_dict

    if main_type == "odometry":
        odom_msg = Status.Odometry()
        odom_msg = msg.odometry

        header_dict = {
            'seq': msg.odometry.header.seq,
            'timestamp': msg.odometry.header.timestamp.ToNanoseconds(),
            'frame_id': msg.odometry.header.frame_id
        }

        point_dict = {
            'x' : msg.odometry.pose.point.x,
            'y' : msg.odometry.pose.point.y,
            'z' : msg.odometry.pose.point.z
        }

        orientation_dict = {
            'x' : msg.odometry.pose.orientation.x,
            'y' : msg.odometry.pose.orientation.y,
            'z' : msg.odometry.pose.orientation.z,
            'w' : msg.odometry.pose.orientation.w
        }

        twist_dict = {
            'x_l': msg.odometry.twist.linear.x,
            'y_l': msg.odometry.twist.linear.y,
            'z_l': msg.odometry.twist.linear.z,
            'x_a': msg.odometry.twist.angular.x,
            'y_a': msg.odometry.twist.angular.y,
            'z_a': msg.odometry.twist.angular.z
        }

        odom_dict = {
            'id_robot': odom_msg.id_robot,
            'header': header_dict,
            'point': point_dict,
            'orientation': orientation_dict,
            'twist': twist_dict
        }
        return "ODOM", odom_dict

def parse_action(action, id_robot):

    action_msg = Action.ActionMessage()
    action_msg.ParseFromString(action)

    if action_msg.id_robot != id_robot:
        return False

    act_msg = Action.MoveLocation()
    if action_msg.action.Is(act_msg.DESCRIPTOR):
        action_msg.action.Unpack(act_msg)
        size = act_msg.size
        loc = act_msg.locations 
        loc_list = []
        for i in loc:
            loc_list.append([i.x,i.y,i.z])

        location_dict = {
            'id_sender': action_msg.id_sender,
            'id_command': action_msg.id_command,
            'size': size,
            'locations': loc_list,
            'status': MoveLocation_dict[act_msg.status]
        }

        return "LOC", location_dict 

    act_msg = Action.MoveBase()
    if action_msg.action.Is(act_msg.DESCRIPTOR):
        action_msg.action.Unpack(act_msg)
        linear = {
            'x': act_msg.x_l,
            'y': act_msg.y_l,
            'z': act_msg.z_l
        }

        angle = {
            'x': act_msg.x_a,
            'y': act_msg.y_a,
            'z': act_msg.z_a
        }

        base_dict = {
            'id_sender': action_msg.id_sender,
            'id_command': action_msg.id_command,
            'linear': linear,
            'angle': angle
        }

        return "BAS", base_dict 

    act_msg = Action.ArmMove()
    if action_msg.action.Is(act_msg.DESCRIPTOR):
        action_msg.action.Unpack(act_msg)
        location = {
            'x': act_msg.x,
            'y': act_msg.y,
            'z': act_msg.z
        }
        
        dimensions = {
            'b': act_msg.b,
            'h': act_msg.h,
            'l': act_msg.l
        }

        armaction = ArmAction_dict[act_msg.armaction]

        arm_dict = {
            'id_sender': action_msg.id_sender,
            'id_command': action_msg.id_command,
            'location': location,
            'dimensions': dimensions,
            'armaction': armaction
        }
        return "ARM", arm_dict 

    # Only happens when there is no valid Message
    return "ERR"

def parse_stream(stream):
    datastream_msg = DataStream.Datastream()
    datastream_msg.ParseFromString(stream)

    id_robot = datastream_msg.id_robot

    stream_msg = DataStream.Image()
    if datastream_msg.datastream.Is(stream_msg.DESCRIPTOR):
        datastream_msg.datastream.Unpack(stream_msg)
        header = DataStream.Image.Header()
        header = stream_msg.header
        timestamp = timestamp_pb2.Timestamp()
        header_dict = {
            'seq': header.seq,
            'timestamp': header.timestamp.ToNanoseconds(),
            'frame_id': header.frame_id
        }
        image_data = [x for x in stream_msg.image_data]

        image_dict = {
            'header' : header_dict,
            'image_data' : image_data,
            'height' : stream_msg.height,
            'width' : stream_msg.width,
            'step' : stream_msg.step,
            'encoding' : stream_msg.encoding,
            'is_bigendian' : stream_msg.is_bigendian
        }

        return "IMAGE", id_robot, image_dict

    stream_msg = DataStream.GMap()
    if datastream_msg.datastream.Is(stream_msg.DESCRIPTOR):
        datastream_msg.datastream.Unpack(stream_msg)
        gmap = io.BytesIO(stream_msg.data)
        return "GMAP", id_robot , gmap

def parse_alive(msg):
    keepalive_msg = KeepAlive.Alive()
    keepalive_msg.ParseFromString(msg)
    return keepalive_msg.id, Alive_dict[keepalive_msg.type]