# This is a sample Python script.

from PIL import Image

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Open bitmap and convert to RGB image with 255 color values
data = Image.open('warehouseSquare.bmp').convert('RGB', colors=256)
pixels = data.load()
object_points = []

# camera & LiDAR data from Object/People Tracking
classification = 'Static'
object_image_x = 370
object_image_y = 0
object_image_width = 185
object_image_height = 1

map_resolution = (544, 544)
camera_position = (335, 220)
camera_angle = 32
camera_resolution = (740, 480)

# assumes that if camera is orientated to right of map, the rotation is 0 degrees
camera_rotation = 225


def trace_objects():
    start_right, stop_right, start_up, stop_up, start_left, stop_left, start_down, stop_down = False, False, False, False, False, False, False, False
    limit_x, limit_y = 0, 0

    # determine camera viewpoint
    camera_viewpoint_x, camera_viewpoint_y = calculate_viewpoints(camera_rotation, map_resolution, camera_position)

    print("camera x: ", camera_position[0], " camera y: ", camera_position[1])
    print("limit x: ", limit_x, " limit_y: ", limit_y)
    print("rotation: ", camera_rotation)
    print("viewpoint: (", camera_viewpoint_x, ", ", camera_viewpoint_y, ")")

    # calculate rotation of first and last ray
    start = camera_rotation + (camera_angle / 2)
    stop = camera_rotation - (camera_angle / 2)

    print("start: ", start)
    print("stop: ", stop)

    # refine search angle by using camera data
    start_correction, stop_correction = refine_camera_angle(object_image_x, object_image_y, object_image_width,
                                                            object_image_height)

    print(start_correction)
    print(stop_correction)

    if start > 360:
        start = start - 360

    if stop < 0:
        stop = 360 + stop

    print("start: ", start)
    print("stop: ", stop)

    start = start - start_correction
    stop = stop + stop_correction

    print("start: ", start)
    print("stop: ", stop)

    # determine first ray
    ray_endpoint_start_x, ray_endpoint_start_y = calculate_viewpoints(start, map_resolution, camera_position)
    print("ray start: (", ray_endpoint_start_x, ", ", ray_endpoint_start_y, ")")

    # determine last ray
    ray_endpoint_stop_x, ray_endpoint_stop_y = calculate_viewpoints(stop, map_resolution, camera_position)
    print("ray stop: (", ray_endpoint_stop_x, ", ", ray_endpoint_stop_y, ")")
    print(" ")

    # determine sides of map where rays start
    if ray_endpoint_start_x == 0:
        start_left = True
    elif ray_endpoint_start_y == 0:
        start_up = True
    elif ray_endpoint_start_x == map_resolution[0] - 1:
        start_right = True
    elif ray_endpoint_start_y == map_resolution[1] - 1:
        start_down = True

    if ray_endpoint_stop_x == 0:
        stop_left = True
    elif ray_endpoint_stop_y == 0:
        stop_up = True
    elif ray_endpoint_stop_x == map_resolution[0] - 1:
        stop_right = True
    elif ray_endpoint_stop_y == map_resolution[1] - 1:
        stop_down = True

    # shoot rays
    shoot_rays(start_right, stop_right, start_up, stop_up, start_left, stop_left, start_down, stop_down,
               ray_endpoint_start_x, ray_endpoint_start_y, ray_endpoint_stop_x, ray_endpoint_stop_y)

    # change color of object pixels that were hit
    classify_object(object_points, classification)

    # look if there are other pixels that belong to the object
    for i in range(0, 100):
        expand_classification(object_points, classification)

    # visualise camera viewpoint
    points = get_ray((camera_position[0], camera_position[1]), (camera_viewpoint_x, camera_viewpoint_y))
    for coordinate in points:
        pixels[coordinate[0], coordinate[1]] = (0, 255, 0)

    # visualise start and end of rays
    points_1 = get_ray((camera_position[0], camera_position[1]),
                       (round(ray_endpoint_start_x), round(ray_endpoint_start_y)))
    points_2 = get_ray((camera_position[0], camera_position[1]),
                       (round(ray_endpoint_stop_x), round(ray_endpoint_stop_y)))

    visualize_ray(points_1, (255, 0, 0))
    visualize_ray(points_2, (255, 0, 0))

    data.show()


def shoot_rays(start_right, stop_right, start_up, stop_up, start_left, stop_left, start_down, stop_down,
               ray_endpoint_start_x, ray_endpoint_start_y, ray_endpoint_stop_x, ray_endpoint_stop_y):
    global object_points

    if start_right and stop_right:
        print("start: right & stop: right")
        for y in range(round(ray_endpoint_start_y), round(ray_endpoint_stop_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_right and stop_up:
        print("start: right & stop: up")
        for y in range(round(ray_endpoint_start_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, ray_endpoint_stop_x):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_right and stop_left:
        print("start: right & stop: left")
        for y in range(round(ray_endpoint_start_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(round(ray_endpoint_stop_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_right and stop_down:
        print("start: right & stop: down")
        for y in range(round(ray_endpoint_start_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", coordinate[0], " y: ", coordinate[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

            print(" ")

        for x in range(round(ray_endpoint_stop_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", coordinate[0], " y: ", coordinate[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_up and stop_right:
        print("start: up & stop: right")
        for x in range(round(ray_endpoint_start_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, round(ray_endpoint_stop_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_up and stop_up:
        print("start: up & stop: up")
        for x in range(round(ray_endpoint_start_x), round(ray_endpoint_stop_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_up and stop_left:
        print("start: up & stop: left")
        for x in range(round(ray_endpoint_start_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(round(ray_endpoint_stop_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_up and stop_down:
        print("start: up & stop: down")
        for x in range(round(ray_endpoint_start_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(round(ray_endpoint_stop_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_left and stop_right:
        print("start: left & stop: right")
        for y in range(0, round(ray_endpoint_start_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, round(ray_endpoint_stop_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_left and stop_up:
        print("start: left & stop: up")
        for y in range(0, round(ray_endpoint_start_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, round(ray_endpoint_stop_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_left and stop_left:
        print("start: left & stop: left")
        for y in range(round(ray_endpoint_stop_y), round(ray_endpoint_start_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_left and stop_down:
        print("start: left & stop: down")
        for y in range(0, round(ray_endpoint_start_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(round(ray_endpoint_stop_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_down and stop_right:
        print("start: down & stop: right")
        for x in range(0, round(ray_endpoint_start_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, round(ray_endpoint_stop_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_down and stop_up:
        print("start: down & stop: up")
        for x in range(0, round(ray_endpoint_start_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for x in range(0, round(ray_endpoint_stop_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_down and stop_left:
        print("start: down & stop: left")
        for x in range(0, round(ray_endpoint_start_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

        for y in range(round(ray_endpoint_stop_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))

    elif start_down and stop_down:
        print("start: down & stop: down")
        for x in range(round(ray_endpoint_start_x), round(ray_endpoint_stop_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                else:
                    visualize_ray_2(coordinate, (0, 0, 255))


def classify_object(coordinates, object_type):
    global pixels

    if object_type == "Static":
        color = (255, 0, 0)
    elif object_type == "Dynamic":
        color = (0, 255, 0)
    else:
        color = (255, 255, 255)

    for coordinate in coordinates:
        pixels[coordinate[0], coordinate[1]] = color


def expand_classification(coordinates, object_type):
    global pixels, object_points

    temp = []

    if object_type == "Static":
        color = (255, 0, 0)
    elif object_type == "Dynamic":
        color = (0, 255, 0)
    else:
        color = (255, 255, 255)

    for coordinate in coordinates:
        if (coordinate[0] + 1) < map_resolution[0]:
            if (pixels[(coordinate[0] + 1), coordinate[1]]) == (255, 255, 255):
                print("expand up")
                pixels[(coordinate[0] + 1), coordinate[1]] = color
                temp.append(((coordinate[0] + 1), coordinate[1]))
        if (coordinate[0] - 1) >= 0:
            if (pixels[(coordinate[0] - 1), coordinate[1]]) == (255, 255, 255):
                print("expand down")
                pixels[(coordinate[0] - 1), coordinate[1]] = color
                temp.append(((coordinate[0] - 1), coordinate[1]))
        if (coordinate[1] + 1) < map_resolution[1]:
            if (pixels[coordinate[0], (coordinate[1] + 1)]) == (255, 255, 255):
                print("expand right")
                pixels[coordinate[0], (coordinate[1] + 1)] = color
                temp.append((coordinate[0], (coordinate[1] + 1)))
        if (coordinate[1] - 1) >= 0:
            if (pixels[coordinate[0], (coordinate[1] - 1)]) == (255, 255, 255):
                print("expand left")
                pixels[coordinate[0], (coordinate[1] - 1)] = color
                temp.append((coordinate[0], (coordinate[1] - 1)))

    for i in temp:
        object_points.append(i)


def refine_camera_angle(object_x, object_y, object_width, object_height):
    # correction, used to make angle not too narrow
    epsilon = 10
    start_correction = ((camera_angle / camera_resolution[0]) * object_x) - 10
    stop_correction = ((camera_angle / camera_resolution[0]) * (camera_resolution[0] - (object_x + object_width))) + 10

    return start_correction, stop_correction


def visualize_ray(points, color):
    global pixels

    for coordinate in points:
        pixels[coordinate[0], coordinate[1]] = color


def visualize_ray_2(coordinate, color):
    global pixels
    pixels[coordinate[0], coordinate[1]] = color


def calculate_viewpoints(rotation, map_resolution, camera_position):
    viewpoint_x, viewpoint_y = 0, 0

    if 0 <= rotation <= 90:
        limit_x = map_resolution[0] - camera_position[0]
        limit_y = camera_position[1]
        temp = limit_y - ((rotation / 360) * (limit_x * 4 + limit_y * 4))
        if temp >= 0:
            viewpoint_y = round(temp)
            viewpoint_x = map_resolution[0] - 1
        else:
            viewpoint_y = 0
            viewpoint_x = round(map_resolution[0] - abs(temp))
            if viewpoint_x < 0:
                viewpoint_x = 0

    elif 90 < rotation <= 180:
        limit_x = camera_position[0]
        limit_y = camera_position[1]
        temp = limit_x - (((rotation - 90) / 360) * (limit_x * 4 + limit_y * 4))
        if temp >= 0:
            viewpoint_x = round(temp)
            viewpoint_y = 0
        else:
            viewpoint_x = 0
            viewpoint_y = round(abs(temp))
    elif 180 < rotation <= 270:
        limit_x = camera_position[0]
        limit_y = map_resolution[1] - camera_position[1]
        temp = camera_position[1] + (((rotation - 180) / 360) * (limit_x * 4 + limit_y * 4))
        if temp <= map_resolution[1]:
            viewpoint_y = round(temp)
            viewpoint_x = 0
            if viewpoint_y > map_resolution[1] - 1:
                viewpoint_y = map_resolution[1] - 1
        else:
            viewpoint_y = map_resolution[1] - 1
            viewpoint_x = round(temp - map_resolution[1])
    elif 270 < rotation <= 360:
        limit_x = map_resolution[0] - camera_position[0]
        limit_y = map_resolution[1] - camera_position[1]
        temp = camera_position[0] + (((rotation - 270) / 360) * (limit_x * 4 + limit_y * 4))
        if temp <= map_resolution[0] - 1:
            viewpoint_x = round(temp)
            viewpoint_y = map_resolution[1] - 1
        else:
            viewpoint_x = map_resolution[0] - 1
            viewpoint_y = round(map_resolution[1] - (temp - map_resolution[0]))
            if viewpoint_y > map_resolution[1] - 1:
                viewpoint_y = map_resolution[1] - 1

    return viewpoint_x, viewpoint_y


def get_ray(start, end):
    # initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # rotate line if difference in y direction is greater than in y direction
    is_steep = abs(dy) > abs(dx)

    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # swap start and en if necessary, store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # calculate error
    error = int(dx / 2.0)
    y_step = 1 if y1 < y2 else -1

    # iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += y_step
            error += dx

    # reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    trace_objects()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/