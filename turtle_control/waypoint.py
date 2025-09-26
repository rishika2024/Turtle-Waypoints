
import rclpy
from rclpy.node import Node


class Waypoint(Node):
    def __init__(self):
        super().__init__("waypoint")
        self.get_logger().info("Waypoint Node")
        self._tmr = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info("Issuing Command!")

def main(args=None):
    rclpy.init(args=args)
    node = Waypoint()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()








