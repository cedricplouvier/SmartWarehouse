# distributed-worldmap

This matlab application provides the possibility to visualise the /odom, /scan and /camera/rgb/image_raw data.
Also the ray tracing progress with the latest odometry data received through the subscriber is shown.

If you are not running this app local you can change your ROS_MASTER_URI by changing the following line:

    rosinit("IP of turtlebot")
    
##### sidenote
The switch is there to prevent errors of unfound topics. Turn the switch off when not connected to a turtlebot to only visualise the ray tracing progress
