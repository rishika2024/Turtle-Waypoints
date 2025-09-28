from geometry_msgs.msg import Twist, Vector3

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_srvs.srv import Empty


class Waypoint(Node):
    def __init__(self):
        super().__init__("waypoint")
        self.get_logger().info("Waypoint Node")        
        self.timeperiod = 0.5
        self.tmr = self.create_timer(self.timeperiod, self.timer_callback)
        self.srv = self.create_service(Empty, 'toggle', self.toggle_callback)
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.MOVING = True
        self.STOP = False
        self.state = self.STOP
        
    def toggle_callback(self, request, response):

        if self.state == self.STOP:
            self.state = self.MOVING
            self.get_logger().info(f"MOVING!!!")

        else:
            self.state = self.STOP
            self.get_logger().info(f"STOPPING!!!")

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




def main(args=None):
    try:
        with rclpy.init(args=args):
            node = Waypoint()

            rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()








