from __future__ import annotations

from typing import Any, Optional
import enum
import time

import dataclasses

@dataclasses.dataclass
class TelemetryPacket:
  timestamp: int
  pitch: int
  roll: int
  yaw: int
  vel_x: int
  vel_y: int
  vel_z: int
  temp_l: int
  temp_h: int
  flight_dist: int
  height: int
  battery: int
  barometer: float
  time: int
  accel_x: float
  accel_y: float
  accel_z: float

  @classmethod
  def from_data_str(self, data: str):
    # There is an ending semicolon
    key_val_pairs = data.split(';')[:-1]
    
    data_dict = {}
    for pair in key_val_pairs:
      key, val = pair.split(':')
      data_dict[key] = val

    return TelemetryPacket(
        timestamp=time.time(),
        pitch=data_dict['pitch'],
        roll=data_dict['roll'],
        yaw=data_dict['yaw'],
        vel_x=data_dict['vgx'],
        vel_y=data_dict['vgy'],
        vel_z=data_dict['vgz'],
        temp_l=data_dict['templ'],
        temp_h=data_dict['temph'],
        height=data_dict['h'],
        flight_dist=data_dict['tof'],
        battery=data_dict['bat'],
        barometer=data_dict['baro'],
        time=data_dict['time'],
        accel_x=data_dict['agx'],
        accel_y=data_dict['agy'],
        accel_z=data_dict['agz']
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

