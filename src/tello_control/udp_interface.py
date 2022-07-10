from __future__ import annotations

from typing import Any, Optional

import logging
import threading
import socket
import time
import queue
import errno

import abc

import cv2

from tello_control import structs

LOGGER = logging.getLogger("tello")


class UdpInterface(abc.ABC):
  """An abstract class for a general UDP Interface

  Attributes:
    messages: A Python Queue which stores messages read from the UDP connection
  """
  def __init__(self, name: str, ip: str, port: int):
    self._name = name
    self._ip = ip
    self._port = port
    self._is_streaming = False

    self.messages = queue.Queue()

  def connect(self) -> None:
    """Connect via UDP.

    This method also creates a thread to continuously wait for and read data
    from the UDP socket.
    """
    LOGGER.info(f"Opening {self._name} UDP Connection")

    self._create_connection()
    self._is_streaming = True

    self._thread = threading.Thread(target=self._receive)
    self._stop_event = threading.Event()
    self._thread.start()

  def disconnect(self) -> None:
    """Disconnect from UDP

    This method stops the thread which is consuming data from the socket.
    """
    if not self._is_streaming:
      raise RuntimeError(
          "Cannot end UDP stream because stream was never\
      started"
      )

    LOGGER.info(f"Closing {self._name} UDP Connection")

    self._stop_event.set()
    self._thread.join()

    self._destroy_connection()
    self._is_streaming = False

  def _receive(self) -> None:
    """Main loop of the UDP Interface which polls data from the UDP interface"""
    while not self._stop_event.is_set():
      msg = self._get_data()
      if msg is not None:
        self.messages.put(msg)

    LOGGER.info(f"Closing {self._name} Receive Thread")

  @abc.abstractmethod
  def _get_data(self) -> Optional[Any]:
    """An abstract method which subclasses use to retrieve data from the
    socket"""
    pass

  @abc.abstractmethod
  def _create_connection(self) -> None:
    """Abstract method which subclasses use to create the UDP socket"""
    pass

  @abc.abstractmethod
  def _destroy_connection(self) -> None:
    """Abstract method which subclasses use to destroy the UDP socket"""
    pass


class UdpSocketInterface(UdpInterface):
  """A UdpInterface representing a traditional UDP socket. Also an abstract
  class"""
  def _create_connection(self) -> None:
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._socket.setblocking(False)
    self._socket.bind(("", self._port))

  def _destroy_connection(self) -> None:
    self._socket.close()

  def _get_data(self) -> Optional[Any]:
    try:
      data, _ = self._socket.recvfrom(1518)
      data = data.decode("utf8").strip()
    except socket.error as e:
      if e.args[0] != errno.EAGAIN:
        LOGGER.error(f"{self._name} encountered socket error {e}")
      return
    except UnicodeDecodeError as e:
      LOGGER.error(f"Could not decode Tello packet: {e}")
      return

    return self._format_packet(data)

  @abc.abstractmethod
  def _format_packet(self, data: str) -> Any:
    """Format a packet from the UDP data

    Args:
      data: Data read from the UDP socket
    """
    pass


class TelemetryInterface(UdpSocketInterface):
  """A UDP socket which processes Tello telemetry

  Attributes:
    history: A list of TelemetryPackets received over the lifetime of the UDP
      connection
  """
  def __init__(self):
    super().__init__("Telemetry", "192.168.10.1", 8890)
    self.history = []

  def _get_data(self) -> Optional[structs.TelemetryPacket]:
    data = super()._get_data()
    if data is not None:
      self.history.append(data)
    return data

  def _format_packet(self, data: str) -> structs.TelemetryPacket:
    return structs.TelemetryPacket.from_data_str(data)


class CommandInterface(UdpSocketInterface):
  """A UDP socket for sending commands to the Tello and receiving responses"""
  def __init__(self):
    super().__init__("Command", "192.168.10.1", 8889)

  def _get_data(self) -> Optional[Any]:
    data = super()._get_data()
    if data is not None:
      LOGGER.debug(f"Received packet '{data[1]}'")
    return data

  def _format_packet(self, data: str) -> tuple[float, str]:
    return time.time(), data

  def send(self, packet: structs.CommandPacket):
    # TODO: Error of socket is not open
    LOGGER.debug(f"Sending {packet}")
    msg = str(packet).encode(encoding="utf-8")
    _ = self._socket.sendto(msg, (self._ip, self._port))


class VideoInterface(UdpInterface):
  """A UdpInterface using OpenCV to open a video socket to the Tello"""
  def __init__(self):
    super().__init__("Video", "0.0.0.0", 11111)

  def _create_connection(self) -> None:
    self._video_capture = cv2.VideoCapture(f"udp://{self._ip}:{self._port}")

  def _destroy_connection(self) -> None:
    self._video_capture.release()

  def _get_data(self) -> Optional[Any]:
    retval, frame = self._video_capture.read()
    if not retval:
      raise RuntimeError("Video Stream disconnected")

    return frame
