def clip_rc(x: float) -> float:
  """Clip RC commands to the [-100, 100] range.

  Tello RC Commands must have an absolute value less than or equal to 100

  Args:
    x: The input to be clipped

  Returns:
    x but clipped to the range [-100, 100].
  """
  return min(max(x, -100), 100)
