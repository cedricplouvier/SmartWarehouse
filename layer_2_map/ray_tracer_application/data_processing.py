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

    # read positional data of static nodes
    with open('data/positional data/static_nodes.json') as json_file:
        data = json.load(json_file)

        for i in data:
            static_nodes["ID"].append(i['ID'])
            static_nodes["position"].append(i['position'])
            static_nodes["orientation"].append(i['orientation'])

    while True:
        camera_data_counter, positional_data_counter, matched_data_counter = 0, 0, 0
        # check availability of camera data
        while len(os.listdir('data/camera data')) == 0:
            print("waiting for camera data.")

        # check availability of positional data
        while len(os.listdir('data/positional data')) == 1:
            print("waiting for positional data.")

        # iterate through data and search for matches (timestamp + nodeID)
        for i in range(len(os.listdir('data/camera data'))):
            # TODO: change to work with multiple objects in one picture
            # read camera data
            with open('data/camera data/camera_data_{}.json'.format(i)) as json_file:
                data = json.load(json_file)

                for k in data:
                    camera_data_ID = k['robot_id']
                    camera_data_timestamp = k['timestamp']
                    classification = k['state']
                    object_image_x = k['x']
                    object_image_y = k['y']
                    object_image_z = k['z']
                    object_image_width = k['width']
                    object_image_height = k['height']

            for j in range(len(os.listdir('data/ positional data'))):
                # read positional data
                with open('data/positional data/positional_data_{}.json'.format(j)) as json_file:
                    data = json.load(json_file)
                    for k in data:
                        positional_data_ID = k['id_robot']
                        positional_data_timestamp = k['header']['timestamp']
                        position = (k['point']['x'], k['point']['y'])
                        orientation = (k['orientation']['x'], k['orientation']['y'], k['orientation']['z'],
                                       k['orientation']['w'])

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

                    os.remove('data/camera data/camera_data_{}.json'.format(i - 1))

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
                    os.remove('data/camera data/camera_data_{}.json'.format(i - 1))
                    os.remove('data/positional data/positional_data_{}.json'.format(j - 1))
