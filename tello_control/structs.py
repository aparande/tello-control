from __future__ import annotations

from typing import Any, Optional
import enum
import time

import dataclasses


@dataclasses.dataclass
class TelemetryPacket:
  timestamp: float
  pitch: int
  roll: int
  yaw: int
  vel_x: int
  vel_y: int
  vel_z: int
  temp_l: int
  temp_h: int
  flight_dist: float
  height: float
  battery: int
  barometer: float
  time: int
  accel_x: float
  accel_y: float
  accel_z: float

  @classmethod
  def from_data_str(cls, data: str):
    # There is an ending semicolon
    key_val_pairs = data.split(';')[:-1]

    data_dict = {}
    for pair in key_val_pairs:
      key, val = pair.split(':')
      data_dict[key] = val

    return TelemetryPacket(
        timestamp=time.time(),
        pitch=int(data_dict['pitch']),
        roll=int(data_dict['roll']),
        yaw=int(data_dict['yaw']),
        vel_x=int(data_dict['vgx']),
        vel_y=int(data_dict['vgy']),
        vel_z=int(data_dict['vgz']),
        temp_l=int(data_dict['templ']),
        temp_h=int(data_dict['temph']),
        height=float(data_dict['h']),
        flight_dist=float(data_dict['tof']),
        battery=int(data_dict['bat']),
        barometer=float(data_dict['baro']),
        time=int(data_dict['time']),
        accel_x=float(data_dict['agx']),
        accel_y=float(data_dict['agy']),
        accel_z=float(data_dict['agz'])
    )


class TelloCommand(enum.Enum):
  SDK_ON = "command"
  START_VIDEO = "streamon"
  STOP_VIDEO = "streamoff"
  TAKE_OFF = "takeoff"
  LAND = "land"
  HOVER = "stop"
  RC = "rc"
  CHECK_BATTERY = "battery?"


@dataclasses.dataclass
class CommandPacket:
  command: TelloCommand
  payload: Optional[list[str]] = None

  def __str__(self) -> str:
    if self.payload is None or len(self.payload) == 0:
      return self.command.value
    return f"{self.command.value} " + " ".join(self.payload)
