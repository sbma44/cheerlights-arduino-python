GE Color Effects Arduino Bridge
===============================

This code allows for control logic of a GE Color Effects string of lights to
be moved to Python, making it easier to manipulate and develop animations.

At the moment the serial link allows for about 23 FPS.  As per http://www.deepdarc.com/2010/11/27/hacking-christmas-lights/ the theoretical max 
refresh rate for the GECE protocol for a string of length 50 is 24 FPS. So, not too
bad.  It's possible that superior performance could be achieved by removing the
ACK step and simply delaying execution. But it's probably not worth the minimal gains.

Please note that all of this code assumes a string of length 50.  Some GECE strings
are 36 nodes long.  You'll need to do a little editing to get this code to work with
them.