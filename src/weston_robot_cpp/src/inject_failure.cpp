#include "weston_robot_cpp/inject_failure.hpp"
// #include "pluginlib/class_list_macros.hpp"
#include "behaviortree_cpp_v3/bt_factory.h"

// // register plugin
// PLUGINLIB_EXPORT_CLASS(weston_robot_cpp::InjectFailure, BT::TreeNode)

// Alternative registration method for BehaviorTree plugins
BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<weston_robot_cpp::InjectFailure>("InjectFailure");
}