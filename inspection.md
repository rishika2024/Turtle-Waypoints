# CRAZY TURTLE
Demonstration package for ME450 Embedded Systems in Robotics.
This README is intentionally vague.
Figuring out how this package works and filling in the details is part of the
exercise. Replace the blanks marked with `${ITEM}` with your answer.
Keep the backticks (\`) but remove the `${}`, so `${ITEM}` becomes `My Answer`.
Unless otherwise specified, list the command and all arguments that you passed to it.

## Repository Configuration
1. The `crazy_turtle` git repository consists of the ROS 2 packages `crazy_turtle` and `crazy_turtle_interfaces`.
2. The package `crazy_turtle` has `<build_type>` of `ament_python`.
2. The package `crazy_turtle_interfaces` has a `<build_type>` of `ament_cmake`.


## Setup Instructions
1. Build the workspace using `mkdir -p ~/me495/src`.
2. Initialize the ROS environment (i.e., set the necessary ROS environment variables) by executing `source /opt/ros/kilted/setup.bash`
3. Make sure no other ROS nodes are running prior to starting by inspecting the results of the ROS command `kill -9 <PID>`.
3. Run the launchfile `go_crazy_turtle.launch.xml` by executing `ros2 launch crazy_turtle go_crazy_turtle.launch.xml`.
4. When running you can see an interactive visual depiction of the ROS graph using the `ros2 run rqt_graph rqt_graph` command.
   The ROS graph, including all topics and node labels, looks like:
   ![[rosgraph.svg](https://github.com/ME495-EmbeddedSystems/homework-1-rishika2024/blob/4ce95935869cfd93c1bffdf174dd20b0da70626a/rosgraph.svg)](${export svg image from the viewer, add it to your homework repository, put path here so it displays in the README.md})

## Runtime Information
The `launchfile` from above should be running at all times when executing the following commands.
If the nodes launched from the `launchfile` are not running, you will get incorrect results.

5. Use the ROS command `ros2 node list` to list all the nodes that are running.
   The output of the command looks like
   ```
   /mover
   /roving_turtle
   /rqt_gui_py_node_6684

   ```
6. Use the ROS command `ros2 topic list` to list the topics
   The output of the command looks like
   ```
   /parameter_events
   /rosout
   /turtle1/cmd_vel
   /turtle1/color_sensor
   /turtle1/pose

   ```

7. Use the ROS command `${command and args}` to verify that the frequency of
   the `/turtle1/cmd_vel` topic is `${frequency} Hz`

8. Use the ROS command `ros2 service list` to list the services.
   The output of the command looks like
   ```
   /clear
   /kill
   /mover/describe_parameters
   /mover/get_parameter_types
   /mover/get_parameters
   /mover/get_type_description
   /mover/list_parameters
   /mover/set_parameters
   /mover/set_parameters_atomically
   /reset
   /roving_turtle/describe_parameters
   /roving_turtle/get_parameter_types
   /roving_turtle/get_parameters
   /roving_turtle/get_type_description
   /roving_turtle/list_parameters
   /roving_turtle/set_parameters
   /roving_turtle/set_parameters_atomically
   /rqt_gui_py_node_6684/describe_parameters
   /rqt_gui_py_node_6684/get_parameter_types
   /rqt_gui_py_node_6684/get_parameters
   /rqt_gui_py_node_6684/get_type_description
   /rqt_gui_py_node_6684/list_parameters
   /rqt_gui_py_node_6684/set_parameters
   /rqt_gui_py_node_6684/set_parameters_atomically
   /spawn
   /switch
   /turtle1/set_pen
   /turtle1/teleport_absolute
   /turtle1/teleport_relative

   ```

9. Use the ROS command `ros2 service type /switch` to determine the type of the `/switch` service, which is `crazy_turtle_interfaces/srv/Switch`.

10. Use the ROS command `ros2 param list` to list the parameters of all running nodes
    ```
    /mover:
     start_type_description_service
     use_sim_time
     velocity
    /roving_turtle:
     background_b
     background_g
     background_r
     holonomic
     qos_overrides./parameter_events.publisher.depth
     qos_overrides./parameter_events.publisher.durability
     qos_overrides./parameter_events.publisher.history
     qos_overrides./parameter_events.publisher.reliability
     start_type_description_service
     use_sim_time
    /rqt_gui_py_node_6684:
     start_type_description_service
     use_sim_time

    ```

11. Use the ROS command `ros2 param describe mover velocity` to get information about the `/mover` `velocity` parameter, including its type, description, and constraints
    ```
    Parameter name: velocity
     Type: double
     Description: The velocity of the turtle
     Constraints:

    ```

12. Use the ROS command `ros2 service call -h` to retrieve a template/prototype for entering parameters for the `/switch` service on the command line.
    ```
    usage: ros2 service call [-h] [--stdin] [-r N]
                         [--qos-profile {unknown,default,system_default,sensor_data,services_default,parameters,parameter_events,action_status_default,best_available,rosout_default}]
                         [--qos-depth N] [--qos-history {system_default,keep_last,keep_all,unknown}] [--qos-reliability {system_default,reliable,best_effort,unknown,best_available}]
                         [--qos-durability {system_default,transient_local,volatile,unknown,best_available}]
                         [--qos-liveliness {system_default,automatic,manual_by_topic,unknown,best_available}]
                         [--qos-liveliness-lease-duration-seconds QOS_LIVELINESS_LEASE_DURATION_SECONDS]
                         service_name service_type [values]

Call a service

positional arguments:
  service_name          Name of the ROS service to call to (e.g. '/add_two_ints')
  service_type          Type of the ROS service (e.g. 'std_srvs/srv/Empty')
  values                Values to fill the service request with in YAML format (e.g. '{a: 1, b: 2}'), otherwise the service request will be published with default values

options:
  -h, --help            show this help message and exit
  --stdin               Read values from standard input
  -r N, --rate N        Repeat the call at a specific rate in Hz
  --qos-profile {unknown,default,system_default,sensor_data,services_default,parameters,parameter_events,action_status_default,best_available,rosout_default}
                        Quality of service preset profile to service client with (default: services_default)
  --qos-depth N         Queue size setting to service client with (overrides depth value of --qos-profile option, default: 10)
  --qos-history {system_default,keep_last,keep_all,unknown}
                        History of samples setting to service client with (overrides history value of --qos-profile option, default: keep_last)
  --qos-reliability {system_default,reliable,best_effort,unknown,best_available}
                        Quality of service reliability setting to service client with (overrides reliability value of --qos-profile option, default: reliable )
  --qos-durability {system_default,transient_local,volatile,unknown,best_available}
                        Quality of service durability setting to service client with (overrides durability value of --qos-profile option, default: volatile )
  --qos-liveliness {system_default,automatic,manual_by_topic,unknown,best_available}
                        Quality of service liveliness setting to service client with (overrides liveliness value of --qos-profile option, default system_default)
  --qos-liveliness-lease-duration-seconds QOS_LIVELINESS_LEASE_DURATION_SECONDS
                        Quality of service liveliness lease duration setting to service client with (overrides liveliness lease duration value of --qos-profile option, default: 0
                        nanoseconds)

    ```

## Package Exploration
1. Use the ROS command `${command and args}` to list the interface types defined by `crazy_turtle_interfaces`
   The output of the command looks like
   ```
   ${list service types here, 1 per line}
   ```
2. Use the ROS command `${command and args}` to list the executables included with the `crazy_turtle` package
   The output of the command looks like
   ```
   ${list executables here, 1 per line}
   ```

## Live Interaction
1. Use the command `${command and args here}` to retrieve the value of the `/mover velocity` parameter, which is `${value here}`.
2. The ROS command to call the `/switch` service is
    ```
    ${enter the command to clal the service with with x=1.3, y=2.1, theta=0.1, angular_velocity=3.1, linear_velocity=4.0}
    ```
3. The return value of the service is (to two decimal places): `x = ${x value} y = ${y value}`.

4. The mover node logged the following information in response to the service call:
   ```
   ${enter each logged message, 1 per line}
   ```
5. What happens to the turtle's motion if you use `${command and args here}` to change `/mover velocity` to 12 while the launchfile is running? `${faster | slower | same}`
6. Use the Linux command `${command and args}` to kill the `/mover` node.
7. Use the ROS command `${command and args}` to start the `/mover` node with a velocity of 12.
    - HINT: Be sure to remap `cmd_vel` to `/turtle1/cmd_vel`.
8. What happened to the turtle's velocity after relaunching `mover`? `${Answer faster OR slower OR same}`
