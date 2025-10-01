from geometry_msgs.msg import Twist
from turtlesim_msgs.msg import Pose
from turtle_interfaces.srv import WayPoints
from turtle_interfaces.msg import ErrorMetric
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from std_srvs.srv import Empty
from turtlesim_msgs.srv import TeleportAbsolute, SetPen
import math

class Waypoint(Node):
    """
    A ROS2 node for controlling turtle movement through waypoints.

    This node - 
    
    1) generats waypoints given a list of points
    2) makes the turtle move to each waypoint in a loop
    3) has a toggle function to start and stop the turtle
    4) publishes error metrics   

    """
    
    def __init__(self):

        """Initialize the Waypoint Node with publishers, subscribers, and services."""

        super().__init__("waypoint")
        self.get_logger().info("Waypoint Node Started")
        
        # Callback group for mutually exclusive callbacks
        self.cbgroup = MutuallyExclusiveCallbackGroup()
        
        # Timer configuration
        self.timeperiod = 0.01
        self.tmr = self.create_timer(self.timeperiod, self.timer_callback)
        
        # Service servers
        self.srv = self.create_service(Empty, 'toggle', self.toggle_callback)
        self.srv_load = self.create_service(WayPoints, 'load', self.load_callback)
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.error_pub = self.create_publisher(ErrorMetric, '/loop_metrics', 10)
        
        # Subscribers
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )
        
        # Service clients
        self.client = self.create_client(Empty, 'reset', callback_group=self.cbgroup)
        self.pen = self.create_client(SetPen, 'turtle1/set_pen', callback_group=self.cbgroup)
        self.teleport = self.create_client(
            TeleportAbsolute, 'turtle1/teleport_absolute', callback_group=self.cbgroup
        )
        
        # State management
        self.MOVING = True
        self.STOP = False
        self.state = self.STOP
        
        # Waypoint management
        self.waypoints_list = []
        self.current_waypoint_index = 0
        self.tolerance = 0.05
        self.distance = 0.0
        
        # Pose tracking
        self.previous_pose = None
        self.current_pose = None
        
        # Performance metrics
        self.count_loop = 0
        self.actual_distance = 0.0
        self.error = 0.0

    def toggle_callback(self, request, response):
        """
        The toggle function for starting and stopping the turtle's movement. 

        """
        if self.state == self.STOP:
            if not self.waypoints_list:
                self.get_logger().error("No waypoints loaded. Load them with the 'load' service.")
                return response
            self.state = self.MOVING
            self.get_logger().info("MOVING!!!")
        else:
            self.state = self.STOP
            self.get_logger().info("STOPPING!!!")
        return response    
    
    def pose_callback(self, pose_msg ):

        """
        The pose function keeps track of the current pose and the previous pose
        It also calculates the actual distance traversed

        """            
        self.previous_pose = self.current_pose
        self.current_pose = pose_msg        
        
        if self.current_pose is not None and self.previous_pose is not None:
            distance_increment = math.dist([self.current_pose.x, self.current_pose.y],[self.previous_pose.x, self.previous_pose.y])
            self.actual_distance += distance_increment
    
    def reach_target(self, target_x = 0.0, target_y = 0.0, current_x = 0.0, current_y = 0.0, current_theta = 0.0): 

        """
        This function implements a p-control-algorithm to reach the target. 

        Args:
        - target_x (float) : the x coordinate of the target position
        - target_y (float) : the y coordinate of the target position
        - current_x (float) : the x coordinate of the current position
        - current_y (float) : the y coordinate of the current position
        - theta (float) : current orientation of the turtle with respect to its x-axis
           


        Returns:
        - True : if the target has been reached
        - False: if target is not reached
        """    
        msg = Twist()
        current_distance = math.dist([target_x, target_y], [current_x, current_y])

        dx = target_x - current_x
        dy = target_y - current_y
        theta_wrt_target = math.atan2(dy, dx)
        theta_error = theta_wrt_target - current_theta
        theta_error = math.atan2(math.sin(theta_error), math.cos(theta_error))

        if current_distance < self.tolerance:
            return True

        if abs(theta_error) > 0.01:
            cmd_vel_theta = theta_error * 2
            msg.angular.z = cmd_vel_theta
            msg.linear.x = 0.0
            msg.linear.y = 0.0
        else: 
            cmd_vel_dist = current_distance * 1.5
            msg.angular.z = 0.0
            msg.linear.x = cmd_vel_dist
            msg.linear.y = 0.0

        self.cmd_vel_pub.publish(msg) 
        return False

    def timer_callback(self): 
        """
    This function controls the turtle's movement with timer tick.
    
    When moving state is active:
    - Guides the turtle to the current target waypoint
    - Advances to next waypoint when current is reached
    - Records performance metrics when completing all waypoints
    
    When stopped state is active:
    - Stops the turtle by publishing zero velocity commands

    Returns:
        None
    """ 
        if self.state == self.MOVING:
            if not self.waypoints_list:
                self.get_logger().error("No waypoints loaded. Load them with the 'load' service.")
                self.state = self.STOP
                return
            
            if self.current_pose is None:
                return
                
            target_x = self.waypoints_list[self.current_waypoint_index].x
            target_y = self.waypoints_list[self.current_waypoint_index].y
            current_x = self.current_pose.x
            current_y = self.current_pose.y
            current_theta = self.current_pose.theta         
            
            waypoint_reached = self.reach_target(target_x=target_x, target_y=target_y, current_x=current_x, current_y=current_y, current_theta=current_theta)
            
            if waypoint_reached:
                self.current_waypoint_index += 1
                if self.current_waypoint_index >= len(self.waypoints_list):
                    self.current_waypoint_index = 0

                    #calculating distance between waypoints in a loop
                    distance = 0.0
                    for i in range(len(self.waypoints_list)-1):
                        p1 = self.waypoints_list[i]
                        p2 = self.waypoints_list[i+1]
                        distance += math.dist([p1.x, p1.y], [p2.x, p2.y])
         
                        
                    distance += math.dist([self.waypoints_list[0].x, self.waypoints_list[0].y], [self.waypoints_list[-1].x, self.waypoints_list[-1].y])
                    self.distance+=distance
         
                 
                    #error metrics:
                    self.count_loop+=1 
                    metric = ErrorMetric()
                    metric.complete_loops = self.count_loop
                    metric.actual_distance = self.actual_distance
                    self.error += abs(self.actual_distance - self.distance)
                    metric.error = self.error            
                    self.error_pub.publish(metric)

                    
        else:
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            msg.linear.y = 0.0
            self.cmd_vel_pub.publish(msg)   
        
    async def draw_x(self, x, y):
        """
        This function is used to draw the x on each waypoint

        Args:
        - x : the x coordinate of the desired waypoint
        - y : the y coordinate of the desired waypoint     
        
        Returns:
        - None 

        """
        self.get_logger().info(f"Drawing X at ({x}, {y})")    
        
        pen_req = SetPen.Request()
        pen_req.r = 0
        pen_req.g = 0
        pen_req.b = 0
        pen_req.off = 1  
        pen_req.width = 5
        await self.pen.call_async(pen_req)      
        
        teleport_request = TeleportAbsolute.Request()       
        teleport_request.x = x - 0.25
        teleport_request.y = y + 0.25
        teleport_request.theta = 0.0
        await self.teleport.call_async(teleport_request) 
    
        pen_req.off = 0 
        pen_req.width = 5 
        await self.pen.call_async(pen_req)       
        
        teleport_request.x = x + 0.25
        teleport_request.y = y - 0.25
        teleport_request.theta = 0.0
        await self.teleport.call_async(teleport_request) 
    
        pen_req.off = 1
        pen_req.width = 5 
        await self.pen.call_async(pen_req)        
        
        teleport_request.x = x - 0.25
        teleport_request.y = y - 0.25
        teleport_request.theta = 0.0
        await self.teleport.call_async(teleport_request)    
    
        pen_req.off = 0 
        pen_req.width = 5 
        await self.pen.call_async(pen_req)        
        
        teleport_request.x = x + 0.25
        teleport_request.y = y + 0.25
        teleport_request.theta = 0.0
        await self.teleport.call_async(teleport_request) 
    
        pen_req.off = 1
        pen_req.width = 5 
        await self.pen.call_async(pen_req)          
    
        self.get_logger().info("Waypoint drawn")

    async def load_callback(self, request, response):
        """
         This function calls the load service. When the service is called : 
          - It resets the node, takes waypoint inputs,
          - It takes waypoint inputs
          - It draws 'x' on the way points and returns to the first waypoint
          - Finally it calculates the total distance between waypoints in a loop    
        """

        self.get_logger().info("load service started")

        
        reset_req = Empty.Request()        
        await self.client.call_async(reset_req)
        
        self.get_logger().info("/reset complete")

        self.waypoints_list = request.waypoints
        self.current_waypoint_index = 0

        # Lift pen
        pen_req = SetPen.Request()
        pen_req.off = 1
        await self.pen.call_async(pen_req)
    
        # Draw X marks
        for wp in self.waypoints_list:
            await self.draw_x(wp.x, wp.y)

        # Teleport to first waypoint
        teleport_request = TeleportAbsolute.Request()
        teleport_request.x = self.waypoints_list[0].x
        teleport_request.y = self.waypoints_list[0].y
        teleport_request.theta = 0.0
        await self.teleport.call_async(teleport_request)

        # Set pen for path
        pen_req = SetPen.Request()
        pen_req.r = 0
        pen_req.g = 255
        pen_req.b = 0
        pen_req.width = 5
        pen_req.off = 0
        await self.pen.call_async(pen_req)

        # Calculate distance       

        response.distance = self.distance
        
        
        self.get_logger().info(f"Total cycle distance = {self.distance:.2f}")
        self.get_logger().info("Completed all waypoints! Cycling back to start.")
        
        self.count_loop = 0
        self.actual_distance = 0.0
        self.error = 0.0

        self.previous_pose = None
        self.current_pose = None
        

        return response

def main(args=None):
    rclpy.init(args=args)            
    node = Waypoint()                
    rclpy.spin(node)                 
    node.destroy_node()          
    rclpy.shutdown() 

if __name__ == '__main__':
    main()