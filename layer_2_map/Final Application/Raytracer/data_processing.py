import os
import json

matched_data = {}
matched_data['camera'] = []
matched_data['position'] = []

# positional header data
positional_data_timestamp = 0
positional_data_ID = 0

# camera header data
camera_data_timestamp = 0
camera_data_ID = 0

# camera data variables
classification = ''
object_image_x = 0
object_image_y = 0
object_image_z = 0
object_image_width = 0
object_image_height = 0

# positional data variables
position = (0, 0)
orientation = (0, 0, 0, 0)

# file name counters
matched_data_counter = 0
initial_position_counter = 0

# dict of static nodes
static_nodes = {"ID": [], "position": [], "orientation": []}


def main():
    # check availability of camera data
    global matched_data_counter, position, orientation, classification, object_image_x, object_image_y, \
        object_image_z, object_image_width, object_image_height, initial_position_counter, camera_data_timestamp, \
        positional_data_timestamp, camera_data_ID, positional_data_ID, static_nodes

    # # read positional data of static nodes
    # with open('data/positional data/static_nodes.json') as json_file:
    #     data = json.load(json_file)
    #
    #     for i in data:
    #         static_nodes["ID"].append(i['ID'])
    #         static_nodes["position"].append(i['position'])
    #        static_nodes["orientation"].append(i['orientation'])

    while True:
        camera_data_counter, positional_data_counter, matched_data_counter = 0, 0, 0
        # check availability of camera data
        while len(os.listdir('data/camera data')) == 0:
            print("waiting for camera data.")

        # check availability of positional data
        while len(os.listdir('data/positional data')) == 1:
            print("waiting for positional data.")

        camera_file = os.listdir('data/camera data')
        positional_file = os.listdir('data/positional data')

        # iterate through data and search for matches (timestamp + nodeID)
        for i in camera_file:
            # TODO: change to work with multiple objects in one picture
            # read camera data
            with open('data/camera data/' + i) as json_file:
                data = json.load(json_file)
                keys = []

                for x in data.keys():
                    keys.append(x)

                for x in keys:
                    camera_data_ID = data[x]['robot_id']
                    camera_data_timestamp = data[x]['timestamp']
                    classification = data[x]['state']
                    object_image_x = data[x]['x']
                    object_image_y = data[x]['y']
                    object_image_z = data[x]['z']
                    object_image_width = data[x]['width']
                    object_image_height = data[x]['height']
                    print(camera_data_timestamp)

            for j in positional_file:
                # read positional data
                print(j)
                with open('data/positional data/' + j) as json_file:
                    data = json.load(json_file)
                    positional_data_ID = data['id_robot']
                    positional_data_timestamp = data['header']['timestamp']
                    position = (data['point']['x'], data['point']['y'])
                    orientation = (data['orientation']['x'], data['orientation']['y'], data['orientation']['z'],
                                   data['orientation']['w'])
                    print(positional_data_timestamp)

                print("matching data")
                # if node is static --> get positionals data from static nodes dict and delete received file
                if camera_data_ID in static_nodes["ID"]:
                    matched_data['camera'].append({
                        'classification': classification,
                        'object_image_x': object_image_x,
                        'object_image_y': object_image_y,
                        'object_image_z': object_image_z,
                        'object_image_height': object_image_height,
                        'object_image_width': object_image_width
                    })

                    matched_data['position'].append({
                        'position': static_nodes["position"][camera_data_ID - 1],
                        'orientation': static_nodes["orientation"][camera_data_ID - 1]
                    })

                    with open('matched data/matched_data_{}.json'.format(matched_data_counter), 'w') as outfile:
                        json.dump(matched_data, outfile)
                        matched_data_counter += 1

                    os.remove('data/camera data/camera_data_{}.json'.format(i))

                # if match --> merge data, write to file and delete received files
                elif camera_data_timestamp == positional_data_timestamp and camera_data_ID == positional_data_ID:
                    matched_data['camera'].append({
                        'classification': classification,
                        'object_image_x': object_image_x,
                        'object_image_y': object_image_y,
                        'object_image_z': object_image_z,
                        'object_image_height': object_image_height,
                        'object_image_width': object_image_width
                    })

                    matched_data['position'].append({
                        'position': position,
                        'orientation': orientation
                    })

                    with open('matched data/matched_data_{}.json'.format(matched_data_counter), 'w') as outfile:
                        json.dump(matched_data, outfile)
                        matched_data_counter += 1
                    os.remove('data/camera data/' + i)
                    os.remove('data/positional data/' + j)
