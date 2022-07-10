import pathlib
import sys
import time
import threading
import logging

import cv2
import numpy as np

tld = pathlib.Path(__file__).resolve().parent.parent.parent / 'src'
sys.path.append(str(tld))

import tello_control

if __name__ == '__main__':
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  tello = tello_control.Tello()
  if not tello.connect():
    logger.info("Exiting because tello connection failed")
    tello.disconnect()
    sys.exit(1)

  tello.stream_video()
  cv2.imshow('Tello', np.zeros((640, 640, 3)))

  while True:
    frame = tello.video.messages.get()
    cv2.imshow('Tello', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  tello.end_video_stream()

  cv2.destroyAllWindows()

  tello.disconnect()
