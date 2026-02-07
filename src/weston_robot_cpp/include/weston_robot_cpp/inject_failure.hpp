#ifndef WESTON_ROBOT_CPP__INJECT_FAILURE_HPP_
#define WESTON_ROBOT_CPP__INJECT_FAILURE_HPP_

#include <string>
#include "rclcpp/rclcpp.hpp"
#include "behaviortree_cpp_v3/condition_node.h"

namespace weston_robot_cpp
{

// This is a BehaviorTree ConditionNode.
// It returns only SUCCESS or FAILURE and does not perform any long-running action.
// Used for configurable failure injection in mission-level logic.
class InjectFailure : public BT::ConditionNode
{
public:
  InjectFailure(const std::string & name, const BT::NodeConfiguration & conf)
  : BT::ConditionNode(name, conf)
  {
  }

  // No input ports are required because we read directly from a ROS parameter.
  static BT::PortsList providedPorts()
  {
    return {};
  }

  BT::NodeStatus tick() override
  {
    // 1. Retrieve the ROS node handle from the Blackboard.
    //    This is the standard pattern used in Nav2 BT plugins.
    auto node = config().blackboard->get<rclcpp::Node::SharedPtr>("node");

    // 2. Declare the parameter if it has not been declared yet.
    //    Default value: false (no failure injection).
    if (!node->has_parameter("inject_failure")) {
      node->declare_parameter("inject_failure", false);
    }

    // 3. Read the current parameter value.
    bool failure_triggered = false;
    node->get_parameter("inject_failure", failure_triggered);

    // 4. Decision logic.
    //    If enabled, return FAILURE to trigger recovery or abort logic in the BT.
    if (failure_triggered) {
      RCLCPP_WARN(
        node->get_logger(),
        "[InjectFailure] Failure injection triggered (Safety gating active).");
      return BT::NodeStatus::FAILURE;
    }

    // Normal execution path.
    return BT::NodeStatus::SUCCESS;
  }
};

}  // namespace weston_robot_cpp

#endif  // WESTON_ROBOT_CPP__INJECT_FAILURE_HPP_
