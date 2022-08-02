from __future__ import annotations

import enum
import time

import dataclasses


@dataclasses.dataclass
class TelemetryPacket:
  """Container for Tello Telemetry.

  All telemetry points are specified in the `Tello SDK User
  Manual
  <https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf>`_

  Args:
    timestamp: When the Telemetry was recorded.
    pitch: the pitch angle of the Tello.
    roll: the roll angle of the Tello.
    yaw: the yaw angle of the Tello.
    vel_x: drone velocity in the x direction.
    vel_y: drone velocity in the y direction.
    vel_z: drone velocity in the z direction.
    temp_l: Corresponds to templ from the SDK
    temp_h: Corresponds to temph from the SDK
    flight_dist: Corresponds to tof from the SDK.
    height: drone height
    battery: drone battery
    barometer: Corresponds to baro from the SDK.
    time: flight time
    accel_x: drone acceleration in the x direction.
    accel_y: drone acceleration in the y direction.
    accel_z: drone acceleration in the z direction.
  """
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
    """Constructs a TelemetryPacket from a string sent by the drone.

    The format of the telemetry coming from the drone is given in the Tello SDK
    User Guide.
    """
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
  """Support commands to send the Tello"""
  SDK_ON = 'command'
  START_VIDEO = 'streamon'
  STOP_VIDEO = 'streamoff'
  TAKE_OFF = 'takeoff'
  LAND = 'land'
  HOVER = 'stop'
  RC = 'rc'
  CHECK_BATTERY = 'battery?'


@dataclasses.dataclass
class CommandPacket:
  """Container for TelloCommands

  Args:
    command: The command name to be sent
    payload: A list of arguments to be sent along with the command name
  """
  command: TelloCommand
  payload: list[str]

  def __str__(self) -> str:
    if len(self.payload) == 0:
      return self.command.value
    return f'{self.command.value} ' + ' '.join(self.payload)


class TelloEvent(enum.Enum):
  """Types of Tello Events"""
  START_CONTROL = 'START_CONTROL'
  STOP_CONTROL = 'STOP_CONTROL'
  DROPPED_PACKET = 'DROPPED_PACKET'
