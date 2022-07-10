from __future__ import annotations
from typing import Optional, Any

import logging
import queue
import time

from tello_control.structs import CommandPacket, TelloCommand
from tello_control.udp_interface import (
    TelemetryInterface, CommandInterface, VideoInterface
)

LOGGER = logging.getLogger("tello")


class Tello:
  """The primary interface between the user and the Tello

  Attributes:
    telem: A UdpInterface for reading Drone Telemetry.
    cmd: A UdpInterface for sending commands and receiving their responses.
    video: A UdpInterface for receiving video frames.
    command_history: A list of command packets sent to the drone.
  """
  def __init__(self, ack_timeout: int = 15):
    self.telem = TelemetryInterface()
    self.cmd = CommandInterface()
    self.video = VideoInterface()
    self.command_history = []

    self._ack_timeout = ack_timeout

  def send_command(
      self,
      command: TelloCommand,
      *args: Any,
      wait_for_success=False
  ) -> tuple[bool, Optional[str]]:
    """Sends a command to the Tello

    Args:
      command: The TelloCommand to send.
      *args: Any arguments the Tello command takes.
      wait_for_success: Whether or not to wait until the Tello response
    """
    str_args = [str(arg) for arg in args]
    packet = CommandPacket(command, payload=str_args)
    self.cmd.send(packet)
    self.command_history.append((time.time(), packet))

    if not wait_for_success:
      return True, None

    # Block until the drone acknowledges
    start = time.time()
    while True:
      try:
        timestamp, msg = self.cmd.messages.get(timeout=self._ack_timeout)
        if timestamp > start:
          return "error" not in msg.lower(), msg
        else:
          continue
      except queue.Empty:
        LOGGER.error(f"Drone did not acknowledge command: {command}")
        return False, None

  @property
  def battery(self) -> int:
    """Check the Tello battery
    """
    ret, msg = self.send_command(
        TelloCommand.CHECK_BATTERY, wait_for_success=True
    )
    if ret and msg is not None:
      return int(msg)
    else:
      raise ValueError("Could not check battery")

  def connect(self) -> bool:
    """Connect to the Tello

    Returns:
      Whether or not the Tello connection was successful
    """
    self.telem.connect()
    self.cmd.connect()
    ret, _ = self.send_command(TelloCommand.SDK_ON, wait_for_success=True)
    return ret

  def stream_video(self):
    """Turn on the video stream"""
    self.send_command(TelloCommand.START_VIDEO, wait_for_success=True)
    self.video.connect()

  def end_video_stream(self):
    """Stop the video stream"""
    self.video.disconnect()
    self.send_command(TelloCommand.STOP_VIDEO, wait_for_success=True)

  def disconnect(self):
    """Disconnect from the tello"""
    self.telem.disconnect()
    self.cmd.disconnect()
