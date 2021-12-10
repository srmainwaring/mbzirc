# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
                        #, ExecuteProcess, IncludeLaunchDescription
from launch.actions import OpaqueFunction
# from launch.actions import RegisterEventHandler
# from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

import subprocess
import codecs

def launch(context, *args, **kwargs):
  robot_name = LaunchConfiguration('name').perform(context)
  robot_model = LaunchConfiguration('model').perform(context)
  x_pos = LaunchConfiguration('x').perform(context)
  y_pos = LaunchConfiguration('y').perform(context)
  z_pos = LaunchConfiguration('z').perform(context)
  r_rot = LaunchConfiguration('R').perform(context)
  p_rot = LaunchConfiguration('P').perform(context)
  y_rot = LaunchConfiguration('Y').perform(context)

  model_file = os.path.join(
      get_package_share_directory('mbzirc_ign'), 'models', robot_model, 'model.sdf.erb')
  print("spawning model file: " + model_file)

  # run erb
  process = subprocess.Popen(['erb', 'name=' + robot_name, model_file], stdout=subprocess.PIPE)
  stdout = process.communicate()[0]
  str_output = codecs.getdecoder("unicode_escape")(stdout)[0]

  ignition_spawn_entity = Node(
      package='ros_ign_gazebo',
      executable='create',
      output='screen',
      arguments=['-string', str_output,
                 '-name', robot_name,
                 '-allow_renaming', 'false',
                 '-x', x_pos,
                 '-y', y_pos,
                 '-z', z_pos,
                 '-R', r_rot,
                 '-P', p_rot,
                 '-Y', y_rot,
                ],
  )

  return [ignition_spawn_entity]

def generate_launch_description():
    return LaunchDescription([
        # Launch Arguments
        DeclareLaunchArgument(
            'name',
            default_value='',
            description='Name of robot to spawn'),
        DeclareLaunchArgument(
            'model',
            default_value='',
            description='SDF model to spawn'),
        DeclareLaunchArgument(
            'x',
            default_value='0',
            description='X position to spawn'),
        DeclareLaunchArgument(
            'y',
            default_value='0',
            description='y position to spawn'),
        DeclareLaunchArgument(
            'z',
            default_value='0',
            description='z position to spawn'),
        DeclareLaunchArgument(
            'R',
            default_value='0',
            description='R rotation to spawn'),

        DeclareLaunchArgument(
            'P',
            default_value='0',
            description='P rotation to spawn'),
        DeclareLaunchArgument(
            'Y',
            default_value='0',
            description='Y rotation to spawn'),
        # launch setup
        OpaqueFunction(function = launch)
    ])
