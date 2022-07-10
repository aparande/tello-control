Tello Control
=========================================
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tello_control

The `DJI Ryze Tello drone <https://m.dji.com/product/tello>`_ is a relatively low
cost, indoor, commercial drone. It exposes an
`SDK <https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf>`_
which lets users connect to the drone and control it programmatically.

This package implements a subset of the SDK with the specific goal of making it
easy to write feedback controllers for the Tello.

Basic Usage
-----------
The most basic use of Tello Control is to takeoff, land, and send RC commands to the drone.::

  import sys
  import time

  from tello_control import Tello, TelloCommand

  tello = Tello()

  # Try connecting to the Tello
  if not tello.connect():
    print("Could not connect to Tello")
    sys.exit(1)

  # Try commanding the Tello to takeoff
  if not tello.send_command(TelloCommand.TAKE_OFF, wait_for_success=True):
    print("Takeoff failed")
    sys.exit(1)

  start_time = time.time()

  # Fly for 10 seconds
  while time.time() - start_time < 10::
    # Command the Tello in the Z direction
    tello.send_command(TelloCommand.RC, 0, 0, 20, 0)

    # Wait 0.1 seconds between each command
    time.sleep(0.1)

  # Land the Tello
  tello.send_command(TelloCommand.LAND, wait_for_success=True)

  # Disconnect from the Tello
  tello.disconnect()

