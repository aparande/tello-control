from __future__ import annotations

import abc
import logging
import threading
import time

from tello_control.structs import TelemetryPacket, TelloCommand
from tello_control import utils

LOGGER = logging.getLogger("controller")


class TelloController:
  def __init__(self, tello, control_frequency: float = 10):
    self._tello = tello
    self._telem_lock = threading.Lock()
    self._pending_telem = []
    self._control_frequency = control_frequency

  def start(self):
    self._control_thread = threading.Thread(target=self._run)
    self._telem_thread = threading.Thread(target=self._process_telem)
    self._stop_event = threading.Event()

    self._control_thread.start()
    self._telem_thread.start()

    self._start_time = time.time()
    LOGGER.info(f"Starting control at {self._start_time}")

  def stop(self):
    self._stop_event.set()

    self._telem_thread.join()
    self._control_thread.join()

    self._end_time = time.time()
    LOGGER.info(f"Ending control at {self._start_time}")

  def _run(self):
    while not self._stop_event.is_set():
      self._telem_lock.acquire()

      try:
        ux, uy, uz, ua = self.step(self._pending_telem)
        ux = utils.clip_rc(ux)
        uy = utils.clip_rc(uy)
        uz = utils.clip_rc(uz)
        ua = utils.clip_rc(ua)

        self._tello.send_command(TelloCommand.RC, ux, uy, uz, ua)
      except Exception as e:
        LOGGER.error(f"Landing tello due to error: {e}")
        self.stop()

      self._pending_telem = []
      self._telem_lock.release()

      time.sleep(1 / self._control_frequency)

  def _process_telem(self):
    while not self._stop_event.is_set():
      # Blocks until something is available
      telem = self._tello.telem.messages.get()

      # Acquire the lock to add to the pending telemetry
      self._telem_lock.acquire()
      self._pending_telem.append(telem)
      self._telem_lock.release()

  @abc.abstractmethod
  def step(
      self, telemetry: list[TelemetryPacket]
  ) -> tuple[float, float, float, float]:
    pass
