from PIL import Image
import numpy as np
import json
import os
import time
import cv2

map_resolution = (4096, 4032)
warehouse_resolution = (20, 10)
camera_origin = (-26.2, -25.56)
resolution = 0.01
camera_angle = 90
camera_resolution = (740, 480)


def trace_objects(data, pixels, classification, object_image_x, object_image_z, object_image_width,
                  camera_relative_position,
                  camera_orientation, map_rotation):
    start_right, stop_right, start_up, stop_up, start_left, stop_left, start_down, stop_down = False, False, False, \
                                                                                               False, False, False, \
                                                                                               False, False
    limit_x, limit_y = 0, 0
    object_points = []

    # calculate camera start position
    camera_start_position = (-(camera_origin[0] / resolution), map_resolution[1] + (camera_origin[1] / resolution))
    # calculate position of camera in map
    print("start position: ", camera_start_position)
    print("relative x:", camera_relative_position[0])
    print("relative y:", camera_relative_position[1])

    # point rotation to compensate for map rotation
    if camera_relative_position[0] < 0 or camera_relative_position[1] < 0:
        map_rotation = -map_rotation

    x_transformed = (camera_relative_position[0] / resolution) * np.cos(np.deg2rad(map_rotation)) - \
                    (camera_relative_position[1] / resolution) * np.sin(np.deg2rad(map_rotation))

    y_transformed = (camera_relative_position[0] / resolution) * np.sin(np.deg2rad(map_rotation)) + \
                    (camera_relative_position[1] / resolution) * np.cos(np.deg2rad(map_rotation))

    # camera is placed downwards wrt rotation of map
    if camera_relative_position[0] < 0 or camera_relative_position[1] < 0:
        map_rotation = -map_rotation

    print("transformed x: ", x_transformed)
    print("transformed y: ", y_transformed)

    camera_position = (camera_start_position[0] + x_transformed, camera_start_position[1] + y_transformed)

    print("position: ", camera_position)

    # calculate orientation of camera in map (convert from quaternion to euler angle)
    camera_rotation = quaternion_to_euler(camera_orientation) + map_rotation

    print("rotation: ", camera_rotation)

    if classification == "static":
        # determine camera viewpoint
        camera_viewpoint_x, camera_viewpoint_y = calculate_viewpoints(camera_rotation, camera_position, None)

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
        start_correction, stop_correction = refine_camera_angle(object_image_x, object_image_width)

        print("correction start: ", start_correction)
        print("correction stop: ", stop_correction)

        # TODO: uncomment to allow angle refining
        start = start - start_correction
        stop = stop + stop_correction

        if start > 360:
            start = start - 360

        if stop < 0:
            stop = 360 + stop

        print("start: ", start)
        print("stop: ", stop)

        # determine first ray
        ray_endpoint_start_x, ray_endpoint_start_y = calculate_viewpoints(start, camera_position, None)
        print("ray start: (", ray_endpoint_start_x, ", ", ray_endpoint_start_y, ")")

        # determine last ray
        ray_endpoint_stop_x, ray_endpoint_stop_y = calculate_viewpoints(stop, camera_position, None)
        print("ray stop: (", ray_endpoint_stop_x, ", ", ray_endpoint_stop_y, ")")
        print(" ")

        # determine side of map where rays start and stop
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
        object_points = shoot_rays(camera_position, pixels, start_right, stop_right, start_up, stop_up, start_left,
                                   stop_left, start_down, stop_down, object_points,
                                   ray_endpoint_start_x, ray_endpoint_start_y, ray_endpoint_stop_x, ray_endpoint_stop_y)

        # print(object_points)

        # print(object_points)
        # print(classification)

        # change color of object pixels that were hit
        classify_object(object_points, classification, pixels)

        # TODO: fix expansion
        # look if there are other pixels that belong to the object
        # for i in range(0, 10):
        # object_points = expand_classification(object_points, classification, pixels)

        # visualise camera viewpoint
        # points = get_ray((camera_position[0], camera_position[1]), (camera_viewpoint_x, camera_viewpoint_y))
        # for coordinate in points:
        # pixels[coordinate[0], coordinate[1]] = (0, 255, 0)

        # visualise start and end of rays
        # points_1 = get_ray((camera_position[0], camera_position[1]),
        # (round(ray_endpoint_start_x), round(ray_endpoint_start_y)))
        # points_2 = get_ray((camera_position[0], camera_position[1]),
        # (round(ray_endpoint_stop_x), round(ray_endpoint_stop_y)))

        # visualize_ray(points_1, (255, 0, 0), pixels)
        # visualize_ray(points_2, (255, 0, 0), pixels)

    elif classification == "dynamic":
        distance = (object_image_z / 1000) / resolution

        # determine camera viewpoint
        # camera_viewpoint_x, camera_viewpoint_y = calculate_viewpoints(camera_rotation, camera_position, distance)

        # calculate rotation of first and last ray
        start = camera_rotation + (camera_angle / 2)
        stop = camera_rotation - (camera_angle / 2)

        # refine search angle by using camera data
        start_correction, stop_correction = refine_camera_angle(object_image_x, object_image_width)

        if start > 360:
            start = start - 360

        if stop < 0:
            stop = 360 + stop

        start = start - start_correction
        stop = stop + stop_correction

        # determine first ray
        # TODO: fix distance
        ray_endpoint_start_x, ray_endpoint_start_y = calculate_viewpoints(start, camera_position, distance)

        # determine last ray
        ray_endpoint_stop_x, ray_endpoint_stop_y = calculate_viewpoints(stop, camera_position, distance)

        # calculate endpoint distance
        endpoint_distance = np.sqrt(np.power((ray_endpoint_start_x - ray_endpoint_stop_x), 2) + np.power(
            (ray_endpoint_start_y - ray_endpoint_stop_y), 2))

        ray_endpoint_start_x_2, ray_endpoint_start_y_2 = calculate_viewpoints(camera_rotation, (ray_endpoint_start_x,
                                                                                                ray_endpoint_start_y),
                                                                              endpoint_distance)

        ray_endpoint_stop_x_2, ray_endpoint_stop_y_2 = calculate_viewpoints(camera_rotation, (ray_endpoint_stop_x,
                                                                                              ray_endpoint_stop_y),
                                                                            endpoint_distance)

        # shoot rays
        shoot_rays_2(ray_endpoint_start_x, ray_endpoint_start_y, ray_endpoint_stop_x, ray_endpoint_stop_y,
                     ray_endpoint_start_x_2, ray_endpoint_start_y_2, ray_endpoint_stop_x_2, ray_endpoint_stop_y_2,
                     pixels)

    data.save('data/map/layer 2/mapLayer2.png')


def shoot_rays(camera_position, pixels, start_right, stop_right, start_up, stop_up, start_left, stop_left, start_down,
               stop_down, object_points,
               ray_endpoint_start_x, ray_endpoint_start_y, ray_endpoint_stop_x, ray_endpoint_stop_y):
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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, ray_endpoint_stop_x):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(round(ray_endpoint_stop_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(round(ray_endpoint_stop_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", coordinate[0], " y: ", coordinate[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, round(ray_endpoint_stop_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(round(ray_endpoint_stop_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(round(ray_endpoint_stop_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, round(ray_endpoint_stop_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, round(ray_endpoint_stop_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(round(ray_endpoint_stop_x), map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, map_resolution[0]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, round(ray_endpoint_stop_y)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (map_resolution[0] - 1, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(0, map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for x in range(0, round(ray_endpoint_stop_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, 0))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

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
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)

        for y in range(round(ray_endpoint_stop_y), map_resolution[1]):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (0, y))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points

    elif start_down and stop_down:
        print("start: down & stop: down")
        for x in range(round(ray_endpoint_stop_x), round(ray_endpoint_start_x)):
            # calculate ray using Bresenham's line algorithm
            points = get_ray((camera_position[0], camera_position[1]), (x, map_resolution[1] - 1))
            for coordinate in points:
                # print("x: ", i[0], " y: ", i[1])
                if pixels[coordinate[0], coordinate[1]] == (255, 255, 255):
                    object_points.append(coordinate)
                    break
                # else:
                # visualize_ray_2(coordinate, (0, 0, 255), pixels)
        return object_points


def shoot_rays_2(ray_endpoint_start_x, ray_endpoint_start_y, ray_endpoint_stop_x, ray_endpoint_stop_y,
                 ray_endpoint_start_x_2, ray_endpoint_start_y_2, ray_endpoint_stop_x_2, ray_endpoint_stop_y_2, pixels):
    points = get_ray((ray_endpoint_start_x, ray_endpoint_start_y), (ray_endpoint_stop_x, ray_endpoint_stop_y))
    points2 = get_ray((ray_endpoint_start_x, ray_endpoint_start_y), (ray_endpoint_start_x_2, ray_endpoint_start_y_2))
    points3 = get_ray((ray_endpoint_start_x_2, ray_endpoint_start_y_2), (ray_endpoint_stop_x_2, ray_endpoint_stop_y_2))
    points4 = get_ray((ray_endpoint_stop_x_2, ray_endpoint_stop_y_2), (ray_endpoint_stop_x, ray_endpoint_stop_y))
    for (i, j, k, l) in zip(points, points2, points3, points4):
        # print("x: ", i[0], " y: ", i[1])
        square_points_1 = get_ray(k, i)
        square_points_2 = get_ray(j, l)
        square_points_3 = get_ray(i, j)
        square_points_4 = get_ray(k, l)
        visualize_ray_2(i, (0, 255, 0), pixels)
        visualize_ray_2(j, (0, 255, 0), pixels)
        visualize_ray_2(k, (0, 255, 0), pixels)
        visualize_ray_2(l, (0, 255, 0), pixels)
        visualize_ray(square_points_1, (0, 255, 0), pixels)
        visualize_ray(square_points_2, (0, 255, 0), pixels)
        visualize_ray(square_points_3, (0, 255, 0), pixels)
        visualize_ray(square_points_4, (0, 255, 0), pixels)


def classify_object(coordinates, object_type, pixels):
    print("classify")
    if object_type == "static":
        color = (255, 0, 0)
    elif object_type == "dynamic":
        color = (0, 255, 0)
    else:
        color = (255, 255, 255)

    for coordinate in coordinates:
        pixels[coordinate[0], coordinate[1]] = color


def expand_classification(coordinates, object_type, pixels):
    temp = []
    print("expand classification")
    if object_type == "Static":
        color = (255, 0, 0)
    elif object_type == "Dynamic":
        color = (0, 255, 0)
    else:
        color = (255, 255, 255)

    for coordinate in coordinates:
        if (coordinate[0] + 1) < map_resolution[0]:
            if (pixels[(coordinate[0] + 1), coordinate[1]]) == (255, 255, 255):
                # print("expand up")
                pixels[(coordinate[0] + 1), coordinate[1]] = color
                temp.append(((coordinate[0] + 1), coordinate[1]))
        if (coordinate[0] - 1) >= 0:
            if (pixels[(coordinate[0] - 1), coordinate[1]]) == (255, 255, 255):
                # print("expand down")
                pixels[(coordinate[0] - 1), coordinate[1]] = color
                temp.append(((coordinate[0] - 1), coordinate[1]))
        if (coordinate[1] + 1) < map_resolution[1]:
            if (pixels[coordinate[0], (coordinate[1] + 1)]) == (255, 255, 255):
                # print("expand right")
                pixels[coordinate[0], (coordinate[1] + 1)] = color
                temp.append((coordinate[0], (coordinate[1] + 1)))
        if (coordinate[1] - 1) >= 0:
            if (pixels[coordinate[0], (coordinate[1] - 1)]) == (255, 255, 255):
                # print("expand left")
                pixels[coordinate[0], (coordinate[1] - 1)] = color
                temp.append((coordinate[0], (coordinate[1] - 1)))

    for i in temp:
        coordinates.append(i)

    return coordinates


def refine_camera_angle(object_x, object_width):
    # correction, used to make angle not too narrow
    start_correction = ((camera_angle / camera_resolution[0]) * object_x)
    stop_correction = ((camera_angle / camera_resolution[0]) * (camera_resolution[0] - (object_x + object_width)))

    return start_correction, stop_correction


def visualize_ray(points, color, pixels):
    for coordinate in points:
        pixels[coordinate[0], coordinate[1]] = color


def visualize_ray_2(coordinate, color, pixels):
    pixels[coordinate[0], coordinate[1]] = color


def calculate_viewpoints(rotation, camera_position, distance):
    global map_resolution
    viewpoint_x, viewpoint_y = 0, 0

    if distance is None:
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

    else:
        if 0 <= rotation <= 90:
            viewpoint_x = (np.cos(np.deg2rad(rotation)) * distance) + camera_position[0]
            viewpoint_y = camera_position[1] - (np.sin(np.deg2rad(rotation)) * distance)

        elif 90 < rotation <= 180:
            viewpoint_x = camera_position[0] - (np.cos(np.deg2rad(180 - rotation)) * distance)
            viewpoint_y = camera_position[1] - (np.sin(np.deg2rad(180 - rotation)) * distance)

        elif 180 < rotation <= 270:
            viewpoint_x = camera_position[0] - (np.cos(np.deg2rad(rotation - 180)) * distance)
            viewpoint_y = camera_position[1] + (np.sin(np.deg2rad(rotation - 180)) * distance)

        elif 270 < rotation <= 360:
            viewpoint_x = camera_position[0] + (np.cos(np.deg2rad(360 - rotation)) * distance)
            viewpoint_y = camera_position[1] + (np.sin(np.deg2rad(360 - rotation)) * distance)

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
    x1 = round(x1)
    x2 = round(x2)
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


def quaternion_to_euler(quaternion):
    t1 = +2.0 * (quaternion[3] * quaternion[2] + quaternion[0] * quaternion[1])
    t2 = +1.0 - 2.0 * (quaternion[1] * quaternion[1] + quaternion[2] * quaternion[2])

    z = np.rad2deg(np.arctan2(t1, t2))

    print(z)

    if z < 0:
        z = 360 + z

    return z


def get_data():
    files = os.listdir('matched data')
    classification = []
    object_image_x = []
    object_image_z = []
    object_image_width = []
    camera_relative_position = []
    camera_orientation = []

    while len(os.listdir('matched data')) == 0:
        print("waiting for matched data")

    # read all matched data files + delete them
    for i in files:
        with open('matched data/' + i) as json_file:
            data = json.load(json_file)
            classification.append(data['camera'][0]['classification'])
            object_image_x.append(data['camera'][0]['object_image_x'])
            object_image_z.append(data['camera'][0]['object_image_z'])
            object_image_width.append(data['camera'][0]['object_image_width'])
            camera_relative_position.append(data['position'][0]['position'])
            camera_orientation.append(data['position'][0]['orientation'])
            # TODO: uncomment
        os.remove('matched data/' + i)

    return classification, object_image_x, object_image_z, object_image_width, camera_relative_position, camera_orientation


def get_map(counter, previous_map):
    # check if there is a (new) layer 1 map available
    while len(os.listdir('data/map/layer 1')) == 0:
        print("waiting for map layer 1")
        time.sleep(1)

    current_map = len(os.listdir('data/map/layer 1')) - 1

    if counter == 0 or current_map != previous_map:
        # open bitmap and convert to RGB image with 255 color values
        print("reading map layer 1")
        data = Image.open('data/map/layer 1/mapLayer1_{}.bmp'.format(current_map)).convert('RGB', colors=256)
        pixels = data.load()
        opencv_im = cv2.imread('data/map/layer 1/mapLayer1_{}.bmp'.format(current_map))
        previous_map = current_map
        return data, pixels, opencv_im, previous_map
    else:
        while len(os.listdir('data/map/layer 2')) == 0:
            print("waiting for map layer 2")
            time.sleep(1)

        print("reading map layer 2")
        data = Image.open('data/map/layer 2/mapLayer2.png').convert('RGB', colors=256)
        pixels = data.load()
        opencv_im = cv2.imread('data/map/layer 2/mapLayer2.png')
        return data, pixels, opencv_im, previous_map


def calculate_map_rotation(opencv_im):
    # detect lines
    im_gray = cv2.cvtColor(opencv_im, cv2.COLOR_BGR2GRAY)
    im_edges = cv2.Canny(im_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(im_edges, 1, np.pi / 180.0, 90, minLineLength=100, maxLineGap=4)

    angles = []
    remove_angles = []

    # calculate line angles
    for [[x1, y1, x2, y2]] in lines:
        cv2.line(opencv_im, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = np.rad2deg(np.arctan2(y2 - y1, x2 - x1))
        angles.append(angle)

    # keep all angles between 0 and 90 degrees, discard the others
    for i in angles:
        print(i)
        if i < 0 or i > 90:
            remove_angles.append(i)

    for i in remove_angles:
        angles.remove(i)

    # calculate mean of remaining angles
    map_rotation = np.mean(angles)

    # visualize detected lines
    # im_resized = cv2.resize(im, (600, 600))
    # cv2.imshow("Detected lines", im_resized)
    # key = cv2.waitKey(0)

    print("map rotation: ", map_rotation)

    return map_rotation


def main():
    classification_counter = 0
    previous_map = 0
    while True:
        data, pixels, opencv_im, previous_map = get_map(classification_counter, previous_map)

        map_rotation = calculate_map_rotation(opencv_im)

        classification, object_image_x, object_image_z, object_image_width, camera_relative_position, camera_orientation \
            = get_data()

        for i in range(len(classification)):
            trace_objects(data, pixels, classification[i], object_image_x[i], object_image_z[i], object_image_width[i],
                          camera_relative_position[i], camera_orientation[i], map_rotation)
            classification_counter += 1
            data, pixels, opencv_im, previous_map = get_map(classification_counter, previous_map)
            map_rotation = calculate_map_rotation(opencv_im)
