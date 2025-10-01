# ME495 Embedded Systems Homework 1
Author: `Rishika Bera`
1. Use `ros2 launch turtle_control waypoints.launch.xml` to run the code
2. The `ros2 service call /waypoint/load turtle_interfaces/srv/WayPoints "{waypoints: [{x: 3.9, y: 5.4}, {x: 1.4, y: 1.6}, {x: 2.2, y: 9.4}, {x: 7.2, y: 6.1}, {x: 4.0, y: 2.6}, {x: 8.2, y: 1.5}]}"` service loads waypoints for the turtle to follow
3. The `ros2 service call /waypoint/toggle std_srvs/srv/Empty` starts and stops the turtle.
4. Here is a video of the turtle in action.
   
   [`https://github.com/user-attachments/assets/9a1160e5-c077-4f57-bacd-07185e7fcc36`](https://github.com/ME495-EmbeddedSystems/homework-1-rishika2024/issues/1#issue-3471890949)

6. Here is a video when the bag is played.

   ${embed video here, must show up inline in the README.md when rendered on github. Video file itself should be uploaded as a github issue and linked here, not in the repository}`
