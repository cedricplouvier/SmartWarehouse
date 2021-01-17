import ActionMessage_pb2 as ActionMessage
import StatusMessage_pb2 as Status
import DataStreamMessage_pb2 as DataStream
import KeepAlive_pb2 as KeepAlive
import DecodingProto
from google.protobuf import any_pb2
from google.protobuf import timestamp_pb2
import io

from PIL import Image


def serialize_status(id_receiver, id_command, id_robot, status) -> str:
    message_body = Status.Status()
    message_body.id_receiver = id_receiver
    message_body.id_command = id_command
    message_body.id_robot = id_robot
    message_body.status = Status.ActionStatus.Value(status)

    return message_body.SerializeToString()

def serialize_image(id_robot: int, image_dict: {}) -> str:
    """
    Returns serialized protobuf message for the 'image' type.

    Serializes the image taken by a camera on the robot. Can be used in picture or film modus.

    Parameters:

    *  id_robot (int): The id of the receiving robot.

    *  image_dict {}: A dict with all the information of the image that needs to be send 

    Returns:

    *  (bytes) : Serialized protobuf message
    """
    message_body = DataStream.Datastream()
    message_body.id_robot = id_robot

    message_image = DataStream.Image()

    image_header = DataStream.Image.Header()
    image_header.seq = image_dict['seq']

    image_timestamp = timestamp_pb2.Timestamp(seconds=image_dict['seconds'], nanos=image_dict['nanoseconds'])

    image_header.timestamp.CopyFrom(image_timestamp)
    image_header.frame_id = image_dict['frame']

    message_image.header.CopyFrom(image_header)

    #TODO: Set image_data of protobuf
    message_image.image_data = bytes(image_dict['data'])
    message_image.height = image_dict['height']
    message_image.width = image_dict['width']
    message_image.encoding = image_dict['encoding']
    message_image.step = image_dict['step']
    message_image.is_bigendian= image_dict['endian']

    message_body.datastream.CopyFrom(_any_packer(message_image))

    return message_body.SerializeToString()

def serialize_laserscan(id_robot:int, laserscan) -> str:
    message_body = DataStream.Lidar()
    
    message_header = DataStream.Lidar.Header()
    message_header.seq = laserscan.header.seq
    message_header.timestamp.FromNanoseconds(int(str(laserscan.header.stamp)))
    message_header.frame_id = laserscan.header.frame_id

    message_body.angle_min = laserscan.angle_min
    message_body.angle_max = laserscan.angle_max
    message_body.angle_increment = laserscan.angle_increment
    message_body.time_increment = laserscan.time_increment
    message_body.scan_time = laserscan.scan_time
    message_body.range_min = laserscan.range_min
    message_body.range_max = laserscan.range_max

    ranges = laserscan.ranges
    for i in ranges:
        message_body.ranges.add(i)

    intensities = laserscan.intensities
    for i in intensities:
        message_body.intensities.add(i)

    message_body.header.CopyFrom(message_header)
    
    return message_body.SerializeToString()


def serialize_odometry(id_robot, header, point, orientation, twist_l, twist_a):
    """ 
    Returns serialized protobuf message for the 'odometry' message type.


    """
    message_body = Status.Odometry()
    message_body.id_robot = id_robot

    message_header = Status.Odometry.Header()
    message_header.seq = header.seq
    message_header.timestamp.FromNanoseconds(int(str(header.stamp)))
    message_header.frame_id = header.frame_id

    message_pose = Status.Odometry.Pose()

    message_point = Status.Odometry.Pose.Point()
    message_point.x = point.x
    message_point.y = point.y
    message_point.z = point.z

    message_orientation = Status.Odometry.Pose.Quaternion()
    message_orientation.x = orientation.x
    message_orientation.y = orientation.y
    message_orientation.z = orientation.z
    message_orientation.w = orientation.w

    message_pose.point.CopyFrom(message_point)
    message_pose.orientation.CopyFrom(message_orientation)

    message_twist = Status.Odometry.Twist()

    message_vec_lin = Status.Odometry.Twist.Vec3()

    message_vec_lin.x = twist_l.x
    message_vec_lin.y = twist_l.y
    message_vec_lin.z = twist_l.z

    message_vec_angl = Status.Odometry.Twist.Vec3()
    message_vec_angl.x = twist_a.x
    message_vec_angl.y = twist_a.y
    message_vec_angl.z = twist_a.z
    message_twist.linear.CopyFrom(message_vec_lin)
    message_twist.angular.CopyFrom(message_vec_angl)

    message_body.header.CopyFrom(message_header)
    message_body.pose.CopyFrom(message_pose)
    message_body.twist.CopyFrom(message_twist)
    return message_body.SerializeToString()

def serialize_gmap(id_robot: int,  gmap_location: str) -> str:
    """
    Returns serialized protobuf message for the 'gmap' type.

    Serializes the gmap image. First it translates the .pgm file into a .bmp file.
    This is then serialized.

    Parameters:

    *  id_robot (int): The id of the receiving robot.

    *  gmap_location (str): The location of the map that needs to be send 

    Returns:

    *  (bytes) : Serialized protobuf message
    """
    message_body = DataStream.Datastream()
    message_body.id_robot = id_robot

    message_map = DataStream.GMap()

    Image.open(gmap_location).convert('1').save("converterdGMAP.bmp")
    image = Image.open("converterdGMAP.bmp")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format('BMP'))

    message_map.data = image_bytes.getvalue()
    message_body.datastream.CopyFrom(_any_packer(message_map))

    return message_body.SerializeToString()

def serialize_action_location(id_sender, id_command, id_robot, size, locations, status = "GO") -> str:
    """
    Returns serialized protobuf message for the 'location' type.

    Serializes a byte stream generated by protobuf, that describes the next location 
    the robot should visit on the map. To make sure the robot drives to the correct position
    there should first be a gmapping done so that the acl can use generated map.


    Parameters:

    *  id_sender (int): The id of the sender. 
        
    *  id_command (int): Internal command_id counter of sender.

    *  id_robot (int): The id of the receiving robot.

    *  size (int): the total amount of locations the robot should visit
      
    *  locations [(int)] : An array of all the locations the robot should visit

    *  status (str) : Describes how the robot should act. (ABORT, PAUSE, STOP, GO) -> default = GO
    
    Returns:

    *  (bytes) : Serialized protobuf message
    """
    message_body = ActionMessage.ActionMessage()
    message_body.id_sender = id_sender
    message_body.id_command = id_command
    message_body.id_robot = id_robot

    action = ActionMessage.MoveLocation()
    action.status = ActionMessage.MoveLocation.Status.Value(status)
    action.size = size

    for i in locations:
        msg_loc = action.locations.add()
        msg_loc.x = i['x']
        msg_loc.y = i['y']
        msg_loc.z = i['z']

    message_body.action.CopyFrom(_any_packer(action))

    return message_body.SerializeToString()

def serialize_action_movebase(id_sender, id_command, id_robot, linear_v= {'x': 0, 'y': 0,'z':0}, angle_v= {'x':0,'y':0,'z':0}) -> str:
    """
    Returns serialized protobuf message for the 'movebase' type.

    Serializes a byte stream generated by protobuf, that describes the movement of the base. 

    Parameters:

    *  id_sender (int): The id of the sender. 
        
    *  id_command (int): Internal command_id counter of sender.

    *  id_robot (int): The id of the receiving robot.

    *  linear_v {'x',y','z'} -> default {0,0,0}

    *  angle_v {'x','y','z'} -> default {0,0,0}
    
    Returns:

    *  (bytes) : Serialized protobuf message
    """
    message_body = ActionMessage.ActionMessage()
    message_body.id_sender = id_sender
    message_body.id_command = id_command
    message_body.id_robot = id_robot

    action = ActionMessage.MoveBase()

    action.x_l = linear_v['x']
    action.y_l = linear_v['y']
    action.z_l = linear_v['z']

    action.x_a = angle_v['x']
    action.y_a = angle_v['y']
    action.z_a = angle_v['z']

    message_body.action.CopyFrom(_any_packer(action))

    return message_body.SerializeToString()

def serialize_action_arm(id_sender, id_command, id_robot,coord, armaction) -> str:
    message_body = ActionMessage.ActionMessage()
    message_body.id_sender = id_sender
    message_body.id_command = id_command
    message_body.id_robot = id_robot

    action = ActionMessage.ArmMove()
    action.x = coord['x']
    action.y = coord['y']
    action.z = coord['z']

    action.b = coord['b']
    action.h = coord['h']
    action.l = coord['l']

    action.armaction = ActionMessage.ArmMove.ArmAction.Value(armaction)

    message_body.action.CopyFrom(_any_packer(action))

    return message_body.SerializeToString()

def serialize_keepalive(id_robot, type_robot):
    message_body = KeepAlive.Alive()
    message_body.id = id_robot
    message_body.type = KeepAlive.Type.Value(type_robot)
    return message_body.SerializeToString()

def _any_packer(message):
    message_any = any_pb2.Any()
    message_any.Pack(message)
    return message_any
