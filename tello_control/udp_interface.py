from typing import Any

import logging
import threading
import socket
import sys
import time
import queue

import abc

import cv2
import numpy as np

from tello_control import structs


class UdpInterface(abc.ABC):

  def __init__(self, name: str, ip: str, port: int):
    self._name = name
    self._ip = ip
    self._port = port
    self._is_streaming = False

    self.messages = queue.Queue()

  def connect(self) -> None:
    logging.info(f"Opening {self._name} UDP Connection")

    self._create_connection()
    self._is_streaming = True

    self._thread = threading.Thread(target=self._receive)
    self._stop_event = threading.Event()
    self._thread.start()

  def disconnect(self) -> None:
    if not self._is_streaming:
      raise RuntimeError("Cannot end UDP stream because stream was never\
      started")

    logging.info(f"Closing {self._name} UDP Connection")

    self._stop_event.set()
    self._thread.join()

    self._destroy_connection()
    self._is_streaming = False

  def _receive(self) -> None:
    while not self._stop_event.is_set():
      msg = self._get_data()
      if msg is not None:
        self.messages.put(msg)

    logging.info(f"Closing {self._name} Receive Thread")

  @abc.abstractmethod
  def _get_data(self) -> Any:
    pass

  @abc.abstractmethod
  def _create_connection(self) -> None:
    pass

  @abc.abstractmethod
  def _destroy_connection(self) -> None:
    pass


class UdpSocketInterface(UdpInterface):

  def _create_connection(self) -> None:
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._socket.settimeout(10)
    self._socket.bind(('', self._port))

  def _destroy_connection(self) -> None:
    self._socket.close()

  def _get_data(self) -> Any:
    try:
      data, server = self._socket.recvfrom(1518)
    except socket.timeout:
      logging.warning(f"{self._name} Connection timed out")
      return

    data = data.decode('utf8').strip()
    return self._format_packet(data)

  @abc.abstractmethod
  def _format_packet(self, data: str) -> Any:
    pass


class TelemetryInterface(UdpSocketInterface):

  def __init__(self):
    super().__init__("Telemetry", '192.168.10.1', 8890)

  def _format_packet(self, data: str) -> structs.TelemetryPacket:
    return structs.TelemetryPacket.from_data_str(data)


class CommandInterface(UdpSocketInterface):

  def __init__(self):
    super().__init__("Command", '192.168.10.1', 8889)

  def _get_data(self) -> Any:
    data = super()._get_data()
    logging.info(f"Received packet '{data}'")
    return data

  def _format_packet(self, data: str) -> str:
    return data

  def send(self, packet: structs.CommandPacket):
    # TODO: Error of socket is not open
    logging.info(f"Sending {packet}")
    msg = str(packet).encode(encoding="utf-8")
    _ = self._socket.sendto(msg, (self._ip, self._port))


class VideoInterface(UdpInterface):
  def __init__(self):
    super().__init__("Video", '0.0.0.0', 11111)

  def _create_connection(self) -> None:
    self._video_capture = cv2.VideoCapture(f"udp://{self._ip}:{self._port}")

  def _destroy_connection(self) -> None:
    self._video_capture.release()

  def _get_data(self) -> Any:
    retval, frame = self._video_capture.read()
    if not retval:
      raise RuntimeError("Video Stream disconnected")

    return frame
