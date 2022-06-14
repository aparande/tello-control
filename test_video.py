import time
import threading

import cv2
import numpy as np

import tello_control

if __name__ == '__main__':
  tello = tello_control.Tello()
  tello.connect()
  time.sleep(0.1)

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
