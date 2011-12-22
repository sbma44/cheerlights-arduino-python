GE Color Effects Arduino Bridge
===============================

This code allows for control logic of a GE Color Effects string of lights to
be moved to Python, making it easier to manipulate animations and other events.

At the moment the serial link allows for about 23 FPS (theoretical max for the
GECE control protocol is closer to 30), though this is only for hue or intensity
control -- not both. I'm hoping to improve this.