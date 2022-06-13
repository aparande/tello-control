import threading

from tello_control.structs import CommandPacket, TelloCommand

from tello_control.udp_interface import TelemetryInterface, CommandInterface

class Tello:
  def __init__(self):
    self.telem = TelemetryInterface()
    self.cmd = CommandInterface()

  def connect(self):
    self.telem.connect()
    self.cmd.connect()

    self._log_thread = threading.Thread(target=self._log)
    self._stop_event = threading.Event()
    self._log_thread.start()

    self.cmd.send(CommandPacket(TelloCommand.SDK_ON))

  def disconnect(self):
    self.telem.disconnect()
    self.cmd.disconnect()

    self._stop_event.set()
    self._log_thread.join()


  def _log(self):
    while not self._stop_event.is_set():
      while not self.telem.messages.empty():
        packet = self.telem.messages.get()
        print(f"[TELEM]: {packet}")

      while not self.cmd.messages.empty():
        packet = self.cmd.messages.get()
        print(f"[CMD]: {packet}")



