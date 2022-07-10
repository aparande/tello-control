# Tello Control

The [DJI Ryze Tello drone](https://m.dji.com/product/tello) is a relatively low
cost, indoor, commercial drone. It exposes an
[SDK](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
which lets users connect to the drone and control it programmatically.

This package implements a subset of the SDK with the specific goal of making it
easy to write feedback controllers for the Tello.
