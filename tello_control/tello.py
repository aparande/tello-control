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

  def __init__(self, ack_timeout: int=15):
    self.telem = TelemetryInterface()
    self.cmd = CommandInterface()
    self.video = VideoInterface()
    self.command_history = []

    self._ack_timeout = ack_timeout

  def send_command(self, command: TelloCommand, *args: Any,
      wait_for_success=False) -> bool:
    str_args = [str(arg) for arg in args]
    packet = CommandPacket(command, payload=str_args)
    self.cmd.send(packet)
    self.command_history.append((time.time(), packet))

    if not wait_for_success:
      return True

    # Block until the drone acknowledges
    start = time.time()
    while True:
      try:
        timestamp, msg = self.cmd.messages.get(timeout=self._ack_timeout)
        if timestamp > start:
          return "ok" in msg.lower()
        else:
          continue
      except queue.Empty:
        logging.error(f"Drone did not acknowledge command: {command}")
        return False

  def connect(self) -> bool:
    self.telem.connect()
    self.cmd.connect()
    return self.send_command(TelloCommand.SDK_ON, wait_for_success=True)

  def stream_video(self):
    self.send_command(TelloCommand.START_VIDEO, wait_for_success=True)
    self.video.connect()

  def end_video_stream(self):
    self.video.disconnect()
    self.send_command(TelloCommand.STOP_VIDEO, wait_for_success=True)

  def disconnect(self):
    self.telem.disconnect()
    self.cmd.disconnect()
