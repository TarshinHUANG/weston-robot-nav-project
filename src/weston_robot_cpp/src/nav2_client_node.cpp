#include <memory>
#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "nav2_msgs/action/navigate_to_pose.hpp"

using namespace std::chrono_literals;

// Action type: Nav2 "NavigateToPose"
using NavigateToPose = nav2_msgs::action::NavigateToPose;
using GoalHandleNav = rclcpp_action::Client<NavigateToPose>::GoalHandle;

class Nav2ClientNode : public rclcpp::Node
{
public:
  Nav2ClientNode() : Node("nav2_client_node")
  {
    // 1) Create an Action client.
    // Connect to the action server named "navigate_to_pose".
    client_ptr_ = rclcpp_action::create_client<NavigateToPose>(
      this,
      "navigate_to_pose");

    // 2) Create a timer (2 seconds) to give the system time to start up.
    // After 2 seconds, send_goal() will be called.
    timer_ = this->create_wall_timer(
      2000ms, std::bind(&Nav2ClientNode::send_goal, this));

    RCLCPP_INFO(this->get_logger(), "Nav2 client node is ready. Will send a goal soon...");
  }

  void send_goal()
  {
    // Stop the timer (send the goal only once).
    timer_->cancel();

    // 3) Wait for Nav2 action server to be available.
    if (!client_ptr_->wait_for_action_server(10s)) {
      RCLCPP_ERROR(this->get_logger(), "Error: Nav2 action server not available. Did you start Nav2?");
      return;
    }

    // 4) Construct goal message.
    auto goal_msg = NavigateToPose::Goal();

    // Frame: map
    goal_msg.pose.header.frame_id = "map";
    goal_msg.pose.header.stamp = this->now();

    // Target position: (x=2.0, y=2.0)
    goal_msg.pose.pose.position.x = 2.0;
    goal_msg.pose.pose.position.y = 2.0;

    // Orientation: w=1.0 means no rotation (identity quaternion)
    goal_msg.pose.pose.orientation.w = 1.0;

    RCLCPP_INFO(this->get_logger(), "Sending goal: (2.0, 2.0)...");

    // 5) Send goal.
    auto send_goal_options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();

    // Set callback: when the action finishes, call result_callback().
    send_goal_options.result_callback =
      std::bind(&Nav2ClientNode::result_callback, this, std::placeholders::_1);

    client_ptr_->async_send_goal(goal_msg, send_goal_options);
  }

  void result_callback(const GoalHandleNav::WrappedResult & result)
  {
    // 6) Handle result.
    switch (result.code) {
      case rclcpp_action::ResultCode::SUCCEEDED:
        RCLCPP_INFO(this->get_logger(), "Succeeded: robot reached the goal.");
        break;
      case rclcpp_action::ResultCode::ABORTED:
        RCLCPP_ERROR(this->get_logger(), "Aborted: planning failed or the robot got stuck.");
        break;
      case rclcpp_action::ResultCode::CANCELED:
        RCLCPP_ERROR(this->get_logger(), "Canceled.");
        break;
      default:
        RCLCPP_ERROR(this->get_logger(), "Unknown result code.");
        break;
    }

    // Shutdown this node after completion
    rclcpp::shutdown();
  }

private:
  rclcpp_action::Client<NavigateToPose>::SharedPtr client_ptr_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Nav2ClientNode>());
  rclcpp::shutdown();
  return 0;
}
