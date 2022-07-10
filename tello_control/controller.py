from __future__ import annotations

import abc
import logging
import threading
import time

from tello_control.structs import TelemetryPacket, TelloCommand
from tello_control import utils

LOGGER = logging.getLogger("controller")

class TelloController:
  def __init__(self, tello):
    self._tello = tello

  def start(self):
    self._thread = threading.Thread(target=self._run)
    self._stop_event = threading.Event()
    self._thread.start()
    self._start_time = time.time()
    LOGGER.info(f"Starting control at {self._start_time}")

  def stop(self):
    self._stop_event.set()
    self._thread.join()
    self._end_time = time.time()
    LOGGER.info(f"Ending control at {self._start_time}")

  def _run(self):
    while not self._stop_event.is_set():
      telemetry = []
      while not self._tello.telem.messages.empty():
        telemetry.append(self._tello.telem.messages.get())

      try:
        ux, uy, uz, ua = self.step(telemetry)
        ux = utils.clip_rc(ux) 
        uy = utils.clip_rc(uy) 
        uz = utils.clip_rc(uz) 
        ua = utils.clip_rc(ua) 

        self._tello.send_command(TelloCommand.RC, ux, uy, uz, ua)
      except Exception as e:
        LOGGER.error(f"Landing tello due to error: {e}")
        self.stop()

      time.sleep(0.1)

  @abc.abstractmethod
  def step(self, telemetry: list[TelemetryPacket]) -> tuple[float, float, float,
      float]:
    pass

