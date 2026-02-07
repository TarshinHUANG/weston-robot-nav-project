cmake_minimum_required(VERSION 3.8)
project(weston_robot_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
# find pluginlib for Behavior Tree plugins
find_package(pluginlib REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)

# executable file: nav2_client_node
add_executable(nav2_client_node src/nav2_client_node.cpp)

# add dependencies
ament_target_dependencies(nav2_client_node
  rclcpp
  rclcpp_action
  nav2_msgs
  geometry_msgs
)


install(TARGETS
  nav2_client_node  
  DESTINATION lib/${PROJECT_NAME}
)

# Behavior Tree Plugin Library (Failure Injection Node)
add_library(weston_bt_plugins SHARED
  src/inject_failure.cpp
)
ament_target_dependencies(weston_bt_plugins
  rclcpp
  rclcpp_action
  nav2_msgs
  geometry_msgs
  pluginlib
  behaviortree_cpp_v3
)
install(TARGETS weston_bt_plugins
  LIBRARY DESTINATION lib/${PROJECT_NAME}
)

# Install Behavior Tree XML files
install(DIRECTORY behavior_trees/
  DESTINATION share/${PROJECT_NAME}/behavior_trees
)

target_include_directories(weston_bt_plugins PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
