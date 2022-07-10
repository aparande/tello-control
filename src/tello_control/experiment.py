import abc
import dataclasses

import csv
import os
import logging
import pathlib

from tello_control.tello import Tello
from tello_control.structs import TelemetryPacket

TELEM_FIELDS = [field.name for field in dataclasses.fields(TelemetryPacket)]

LOGGER = logging.getLogger("experiment")


class Experiment(abc.ABC):
  """
  Abstract class which provides a framework to analyze a session with the tello.

  Experiments record the telemetry read from the tello and the commands sent to
  the tello to CSVs which can be later analyzed.

  Attributes:
    tello: The Tello which the experiment is being run with.
  """
  def __init__(self, output_path: str):
    self.tello = Tello()
    self._output_path = pathlib.Path(output_path)

  def setUp(self) -> bool:
    """
    Do all setup related to the experiment.

    At a minimum, this method simply connects to the Tello and returns whether
    or not that connection was successful.

    Returns:
      Whether or not connecting to the tello was successful.
    """
    return self.tello.connect()

  def tearDown(self):
    """
    Destroy any objects created during the experiment.

    At a minimum, this method simply disconnects from the Tello.
    """
    self.tello.disconnect()

  def log_results(self):
    """Write the telemetry trace to the experiment output path"""
    if not os.path.exists(self._output_path):
      os.mkdir(self._output_path)

    with open(self._output_path / "trace.csv", "w") as csv_file:
      writer = csv.DictWriter(csv_file, fieldnames=TELEM_FIELDS)

      writer.writeheader()
      for message in self.tello.telem.history:
        writer.writerow(dataclasses.asdict(message))

  def log_command_history(self):
    """Write the command history to the experiment output path"""
    if not os.path.exists(self._output_path):
      os.mkdir(self._output_path)

    with open(self._output_path / "command-history.csv", "w") as csv_file:
      writer = csv.writer(csv_file)
      writer.writerow(["Timestamp", "Command", "Arg0", "Arg1", "Arg2", "Arg3"])
      for timestamp, cmd in self.tello.command_history:
        writer.writerow([timestamp, cmd.command, *cmd.payload])

  def run(self):
    """Run the experiment

    Running an experiment entails setting up the experiment, running the main
    function, and tearing down any created resources.
    """
    if not self.setUp():
      LOGGER.error("Did not run experiment because could not connect to drone")
      return

    self.main()

    self.tearDown()

    self.log_results()
    self.log_command_history()

  @abc.abstractmethod
  def main(self):
    """Main loop of the experiment

    An experiment is created by overriding this method at minimum
    """
    pass
