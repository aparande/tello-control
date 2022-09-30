"""Module for an open loop controller for Tello Yaw"""

from __future__ import annotations
from typing import Callable

from collections.abc import Iterable
import time

from tello_control import Tello, TelloController, TelemetryPacket


class YawOpenLoopController(TelloController):
  """An open loop controller for Tello Yaw"""

  # Constant defining the Open Loop Behavior
  OPEN_LOOP_CONST = 0.43025515

  def __init__(
      self, tello: Tello, reference: Callable[[float], tuple[float, float]]
  ):
    self.reference = reference
    super().__init__(tello)

  def compute_reference(
      self, now_time: float, telemetry: list[TelemetryPacket]
  ) -> Iterable[float]:
    return self.reference(now_time - self.start_time)

  def step(
      self, telemetry: list[TelemetryPacket]
  ) -> tuple[float, float, float, float]:
    _, ref_yaw_vel = self.compute_reference(time.time(), telemetry)

    ua = ref_yaw_vel / self.OPEN_LOOP_CONST
    return 0, 0, 0, ua
