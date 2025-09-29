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
        self.timeperiod = 0.1
        self.tmr = self.create_timer(self.timeperiod, self.timer_callback)
        self.srv = self.create_service(Empty, 'toggle', self.toggle_callback)
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_pub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.current_pose = None

        self.srv_load= self.create_service(WayPoints, 'load', self.load_callback)

        self.MOVING = True
        self.STOP = False
        self.state = self.STOP

        self.client = self.create_client(Empty, '/reset') #to restart turtlesim

        self.pen = self.create_client(SetPen, 'turtle1/set_pen')

        
        self.teleport = self.create_client(TeleportAbsolute, 'turtle1/teleport_absolute')

        self.waypoints_list = []
        self.current_waypoint_index = 0

        self.target_reached = False
        self.target_angle_reached = False

    def toggle_callback(self, request, response):

        if self.state == self.STOP:
            if not self.waypoints_list:
                self.get_logger().error("No waypoints loaded yet, load with load service")
                return response
                
            self.state = self.MOVING
            self.get_logger().info("MOVING!!!")

        else:
            self.state = self.STOP
            self.get_logger().info("STOPPING!!!")

        return response    
    
    def pose_callback(self, msg):

        self.current_pose = msg
    
    def reach_target(self, target_x = 0.0, target_y = 0.0, current_x = 0.0, current_y = 0.0, current_theta = 0.0):
        
        pen_req = SetPen.Request()
        msg = Twist()

        current_distance = math.dist([target_x, target_y], [current_x, current_y])

        dx = target_x - current_x
        dy = target_y - current_y
        theta_wrt_target = math.atan2(dy, dx)
        theta_error = theta_wrt_target-current_theta

         #normalizing so that theta error is between -pi to +pi
        theta_error = math.atan2(math.sin(theta_error), math.cos(theta_error))

        pen_req.r = 255
        pen_req.width = 5

        # If we're close enough to waypoint, mark it as reached

        if current_distance<0.1:
            return True
        

        if abs(theta_error) > 0.01:

            pen_req.off = 1
            cmd_vel_theta = theta_error*2
            msg.angular.z = cmd_vel_theta
            msg.lin .x = 0.0
            msg.linear.y = 0.0
                       

        else: 
            pen_req.off = 0   

            cmd_vel_dist = min(current_distance*1.5, 1.0)
            msg.angular.z = 0.0
            msg.linear.x = cmd_vel_dist
            msg.linear.y = 0.0

        self.cmd_vel_pub.publish(msg) 


    def timer_callback(self):  

        msg = Twist()    

        if self.state == self.MOVING:
            if not self.waypoints_list:
                self.get_logger().error("No waypoints loaded yet, load with load service")
                self.state = self.STOP
                return
            
            if self.current_pose is None:
                return
                
            target_x = self.waypoints_list[self.current_waypoint_index].x
            target_y = self.waypoints_list[self.current_waypoint_index].y
            current_x = self.current_pose.x
            current_y = self.current_pose.y
            current_theta = self.current_pose.theta         
            
            # FIX: Call reach_target every time and check return value
            waypoint_reached = self.reach_target(
                target_x=target_x, 
                target_y=target_y, 
                current_x=current_x, 
                current_y=current_y, 
                current_theta=current_theta
            )
            
            if waypoint_reached:
                self.current_waypoint_index += 1
                if self.current_waypoint_index >= len(self.waypoints_list):
                    self.current_waypoint_index = 0
                    self.get_logger().info("Completed all waypoints!")
               
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            msg.linear.y = 0.0
            self.cmd_vel_pub.publish(msg)   
        
    def draw_x(self, x, y):

        self.get_logger().info(f"Drawing X at ({x}, {y})")    
        
        pen_req = SetPen.Request()
        pen_req.r = 255
        pen_req.g = 255
        pen_req.b = 255
        pen_req.off = 1  
        pen_req.width = 5
        future = self.pen.call_async(pen_req)        
        time.sleep(0.1)
        
        teleport_request = TeleportAbsolute.Request()       
        teleport_request.x = x - 0.25
        teleport_request.y = y + 0.25
        teleport_request.theta = 0.0
        self.teleport.call_async(teleport_request)
        time.sleep(0.1)
    
        
        pen_req.off = 0 
        pen_req.width = 5 
        self.pen.call_async(pen_req)
        time.sleep(0.1)
    
        
        teleport_request.x = x + 0.25
        teleport_request.y = y - 0.25
        teleport_request.theta = 0.0
        self.teleport.call_async(teleport_request)
        time.sleep(0.1)
    
        
        pen_req.off = 1
        pen_req.width = 5 
        future = self.pen.call_async(pen_req)
        time.sleep(0.1)
        
        teleport_request.x = x - 0.25
        teleport_request.y = y - 0.25
        teleport_request.theta = 0.0
        self.teleport.call_async(teleport_request)
        time.sleep(0.1)    
    
        pen_req.off = 0 
        pen_req.width = 5 
        future = self.pen.call_async(pen_req)
        time.sleep(0.1)
    
        
        teleport_request.x = x + 0.25
        teleport_request.y = y + 0.25
        teleport_request.theta = 0.0
        self.teleport.call_async(teleport_request)
        time.sleep(0.1)
    
    
        pen_req.off = 1
        pen_req.width = 5 
        self.pen.call_async(pen_req)
        time.sleep(0.1)
    
        self.get_logger().info("Waypoint")
       


    def load_callback(self, request, response):
        self.get_logger().info("load service")

        if not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().error("/reset not available")
            return response
    

        self.client.call_async(Empty.Request())        
        self.get_logger().info("/reset complete")

        self.waypoints_list = request.waypoints

        for wp in self.waypoints_list:
            self.draw_x(wp.x, wp.y) #drawing x at all the waypoints

        request = TeleportAbsolute.Request() #teleporting the turtle back to the 1st waypoint
        request.x = self.waypoints_list[0].x
        request.y = self.waypoints_list[0].y      
        self.teleport.call_async(request)  
        

        self.state = self.STOP

        distance = 0.0

        for i in range(len(self.waypoints_list)-1):
            p1 = self.waypoints_list[i]
            p2 =  self.waypoints_list[i+1]
            distance+= math.dist([p1.x, p1.y], [p2.x, p2.y])

        distance += math.dist([self.waypoints_list[0].x, self.waypoints_list[0].y], [self.waypoints_list[len(self.waypoints_list)-1].x, self.waypoints_list[len(self.waypoints_list)-1].y ])

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