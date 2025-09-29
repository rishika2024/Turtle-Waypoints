from geometry_msgs.msg import Twist

from turtle_interfaces.srv import WayPoints

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_srvs.srv import Empty

from turtlesim_msgs.srv import TeleportAbsolute

import math



class Waypoint(Node):
    def __init__(self):
        super().__init__("waypoint")
        self.get_logger().info("Waypoint Node")        
        self.timeperiod = 0.5
        self.tmr = self.create_timer(self.timeperiod, self.timer_callback)
        self.srv = self.create_service(Empty, 'toggle', self.toggle_callback)
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.srv_load= self.create_service(WayPoints, 'load', self.load_callback)

        self.MOVING = True
        self.STOP = False
        self.state = self.STOP

        self.client = self.create_client(Empty, '/reset') #to restart turtlesim

        
        self.teleport = self.create_client(TeleportAbsolute, 'turtle1/teleport_absolute')
        
    def toggle_callback(self, request, response):

        if self.state == self.STOP:
            self.state = self.MOVING
            self.get_logger().info("MOVING!!!")

        else:
            self.state = self.STOP
            self.get_logger().info("STOPPING!!!")

        return response    
        

    def timer_callback(self):  

        msg = Twist()      

        self.get_logger().debug(f"Issuing Command!")

        if self.state == self.MOVING:
            msg.linear.x = 5.0
            msg.angular.z = 7.0
            self.cmd_vel_pub.publish(msg)
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.cmd_vel_pub.publish(msg)      

    def draw_x(self, x, y):

        request = TeleportAbsolute.Request()

        request.x = x+1
        request.y = y+1        
        self.teleport.call_async(request)

        request.x = x-1
        request.y = y-1        
        self.teleport.call_async(request)

        request.x = x
        request.y = y        
        self.teleport.call_async(request)

        request.x = x-1
        request.y = y+1        
        self.teleport.call_async(request)

        request.x = x+1
        request.y = y-1        
        self.teleport.call_async(request)

        request.x = x
        request.y = y        
        self.cli.call_async(request)    
    


    def load_callback(self, request, response):
        self.get_logger().info("load service")

        rclpy.spin_until_future_complete(self, self.client.call_async(Empty.Request()))

        waypoints = request.waypoints

        for wp in waypoints:
            self.draw_x(wp.x, wp.y) #drawing x at all the waypoints

        request = TeleportAbsolute.Request() #teleporting the turtle back to the 1st waypoint
        request.x = waypoints[0].x
        request.y = waypoints[0].y        
        self.teleport.call_async(request)

        self.state = self.STOP

        distance = 0.0

        for i in range(len(waypoints)-1):
            p1 = waypoints[i]
            p2 =  waypoints[i+1]
            distance+= math.dist([p1.x, p1.y], [p2.x, p2.y])

        distance += math.dist([waypoints[0].x, waypoints[0].y], [waypoints[len(waypoints)-1].x,waypoints[len(waypoints)-1].y ])

        response.distance = distance

        self.get_logger().info(f"Total cycle distance = {distance:.2f}")
        return response

        
def main(args=None):
    rclpy.init(args=args)            
    node = Waypoint()                
    rclpy.spin(node)                 
    node.destroy_node()          
    rclpy.shutdown() 

if __name__ == '__main__':
    main()








