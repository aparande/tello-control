import abc
import dataclasses

import csv
import os
import time
import threading
import logging
import pathlib

from tello_control.tello import Tello
from tello_control.structs import TelloCommand, TelemetryPacket

TELEM_FIELDS = [field.name for field in dataclasses.fields(TelemetryPacket)]

class Experiment(abc.ABC):
  def __init__(self, output_path: str):
    self.tello = Tello()
    self._output_path = pathlib.Path(output_path)

  def setUp(self):
    self.tello.connect()

  def tearDown(self):
    self.tello.disconnect()

  def log_results(self):
    if not os.path.exists(self._output_path):
      os.mkdir(self._output_path)

    with open(self._output_path / "trace.csv", 'w') as csv_file:
      writer = csv.DictWriter(csv_file, fieldnames=TELEM_FIELDS)

      writer.writeheader()
      while not self.tello.telem.messages.empty():
        message = self.tello.telem.messages.get()
        writer.writerow(dataclasses.asdict(message))

  def run(self):
    self.setUp()

    logging.info("Connecting to Tello...")
    time.sleep(1)

    self.main()

    self.tearDown()

    self.log_results()

  @abc.abstractmethod
  def main(self):
    pass

