# SmartWarehouse
## Functionality
Purpose is for a robot to receive a retrieval task in a warehouse. Navigate to it's correct location, recognize the object through vision AI and bring it back to the docking station while using the optimal rout and avoiding dynimic collisions.

## Implementation
An object detection model is deployed on the robot to detect to object.
To navigate the robot through the warehouse a mapping of the floorplan is generated using SLAM.
Wihle navigating the LIDAR sensor is used to detect dynmic objects on it's path and re-route if necessary. Taking into account the dynamic object moving direction and speed.
A digital twin is created based on the warehouse floorplan generate with SLAM to make the robot navigate autonomously.

<img width="701" alt="Screenshot 2025-05-22 at 15 54 04" src="https://github.com/user-attachments/assets/6cbfe9ac-d9c8-41e6-8d8b-b6b37e619f1e" />
