from typing import Optional, Any

import logging
import threading
import time
import queue

import cv2
import numpy as np

from tello_control.structs import CommandPacket, TelloCommand
from tello_control.udp_interface import (TelemetryInterface, CommandInterface,
                                         VideoInterface)


class Tello:

  def __init__(self):
    self.telem = TelemetryInterface()
    self.cmd = CommandInterface()
    self.video = VideoInterface()

  def send_command(self, command: TelloCommand, *args: Any):
    str_args = [str(arg) for arg in args]
    self.cmd.send(CommandPacket(command, payload=str_args))

  def connect(self):
    self.telem.connect()
    self.cmd.connect()
    self.cmd.send(CommandPacket(TelloCommand.SDK_ON))

  def stream_video(self):
    self.cmd.send(CommandPacket(TelloCommand.START_VIDEO))
    self.video.connect()

  def end_video_stream(self):
    self.video.disconnect()
    self.cmd.send(CommandPacket(TelloCommand.STOP_VIDEO))

  def disconnect(self):
    self.telem.disconnect()
    self.cmd.disconnect()
