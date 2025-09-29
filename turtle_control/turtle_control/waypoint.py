from geometry_msgs.msg import Twist
from turtlesim_msgs.msg import Pose

from turtle_interfaces.srv import WayPoints

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_srvs.srv import Empty

from turtlesim_msgs.srv import TeleportAbsolute, SetPen

import math
import time



class Waypoint(Node):
    def __init__(self):
        super().__init__("waypoint")
        self.get_logger().info("Waypoint Node")        
        self.timeperiod = 0.5
        self.tmr = self.create_timer(self.timeperiod, self.timer_callback)
        self.srv = self.create_service(Empty, 'toggle', self.toggle_callback)
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        #self.pose_pub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.current_pose = None

        self.srv_load= self.create_service(WayPoints, 'load', self.load_callback)

        self.MOVING = True
        self.STOP = False
        self.state = self.STOP

        self.client = self.create_client(Empty, '/reset') #to restart turtlesim

        self.pen = self.create_client(SetPen, 'turtle1/set_pen')

        
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

        self.get_logger().info(f"Drawing X at ({x}, {y})")
    
        # First, lift pen and move to starting position
        pen_req = SetPen.Request()
        """pen_req.off = 1  # Lift pen
        pen_req.width = 5 
        self.pen.call_async(pen_req)        
        time.sleep(0.1)"""
        
        teleport_request = TeleportAbsolute.Request()       
        teleport_request.x = x - 0.5
        teleport_request.y = y + 0.5
        teleport_request.theta = 0.0
        self.teleport.call_async(teleport_request)
        time.sleep(0.1)
    
        # Lower pen for first diagonal
        pen_req.off = 0  # Lower pen
        pen_req.width = 5 
        self.pen.call_async(pen_req)
        time.sleep(0.1)
    
        # Draw first diagonal (top-left to bottom-right)
        teleport_request.x = x + 0.5
        teleport_request.y = y - 0.5
        teleport_request.theta = 0.0
        self.teleport.call_async(teleport_request)
        time.sleep(0.1)
    
        # Lift pen and move to start of second diagonal
        pen_req.off = 1  # Lift pen
        pen_req.width = 5 
        future = self.pen.call_async(pen_req)
        time.sleep(0.1)
        
        teleport_request.x = x - 0.5
        teleport_request.y = y - 0.5
        teleport_request.theta = 0.0
        self.teleport.call_async(teleport_request)
        time.sleep(0.1)
    
        # Lower pen for second diagonal
        pen_req.off = 0  # Lower pen
        pen_req.width = 5 
        future = self.pen.call_async(pen_req)
        time.sleep(0.1)
    
        # Draw second diagonal (bottom-left to top-right)
        teleport_request.x = x + 0.5
        teleport_request.y = y + 0.5
        teleport_request.theta = 0.0
        self.teleport.call_async(teleport_request)
        time.sleep(0.1)
    
        # Lift pen at the end
        pen_req.off = 1  # Lift pen
        pen_req.width = 5 
        self.pen.call_async(pen_req)
        time.sleep(0.1)
    
        self.get_logger().info("X set")
    

    


    def load_callback(self, request, response):
        self.get_logger().info("load service")

        if not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().error("/reset not available")
            return response
    

        self.client.call_async(Empty.Request())
        
        self.get_logger().info("/reset complete")

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