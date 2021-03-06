import logging
import pathlib
import sys
import time

tld = pathlib.Path(__file__).resolve().parent.parent.parent / 'src'
sys.path.append(str(tld))

from tello_control import Tello

if __name__ == "__main__":
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  tello = Tello()

  if not tello.connect():
    logger.info("Exiting because tello connection failed")
    tello.disconnect()
    sys.exit(1)

  start = time.time()
  while True:
    message = tello.telem.messages.get()
    print(message)

    if time.time() - start > 10:
      break

  tello.disconnect()
