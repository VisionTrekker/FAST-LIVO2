#!/usr/bin/python3
# -- coding: utf-8 --**

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    # Find path
    config_file_dir = os.path.join(get_package_share_directory("fast_livo"), "config")
    rviz_config_file = os.path.join(get_package_share_directory("fast_livo"), "rviz_cfg", "fast_livo2.rviz")

    # Load parameters
    camera_config_cmd = os.path.join(config_file_dir, "camera_pinhole.yaml")

    # Param use_rviz
    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="False",
        description="Whether to launch Rviz2",
    )

    # Param use_respawn
    use_respawn_arg = DeclareLaunchArgument(
        "use_respawn",
        default_value="True",
        description="Whether to respawn if a node crashes.",
    )

    # 默认 go2w；要切到 car 就 `mid360_config_name:=mid360_car.yaml`
    mid360_config_name_arg = DeclareLaunchArgument(
        "mid360_config_name",
        default_value="mid360_go2w.yaml",
        description=(
            "MID360 config filename (must live in fast_livo/config/). "
            "E.g. mid360_go2w.yaml, mid360_car.yaml."
        ),
    )

    camera_config_arg = DeclareLaunchArgument(
        "camera_params_file",
        default_value=camera_config_cmd,
        description="Full path to the ROS2 parameters file for camera",
    )

    mid360_config_name = LaunchConfiguration("mid360_config_name")
    camera_params_file = LaunchConfiguration("camera_params_file")
    use_respawn = LaunchConfiguration("use_respawn")

    return LaunchDescription([
        use_rviz_arg,
        use_respawn_arg,
        mid360_config_name_arg,
        camera_config_arg,

        # FAST-LIVO2 LIO-only node
        # Node.parameters 接受 substitution list: 框架会把 [config_file_dir, "/",
        # mid360_config_name] 自动 join 成单个 yaml 路径字符串。
        # 完全没有 OpaqueFunction / PythonExpression / eval。
        Node(
            package="fast_livo",
            executable="fastlivo_mapping",
            name="laserMapping",
            parameters=[
                [config_file_dir, "/", mid360_config_name],
                camera_params_file,
            ],
            output="screen"
        ),

        Node(
            condition=IfCondition(LaunchConfiguration("use_rviz")),
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", rviz_config_file],
            output="screen"
        ),
    ])
