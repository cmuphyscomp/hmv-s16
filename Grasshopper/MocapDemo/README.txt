2016-01-18

This is a self-contained demo of receiving real-time Optitrack motion capture rigid body data.

Files:

MocapDemo.gh	Grasshopper patch for the demo
demo.py		reference copy of ghpython code from MocapDemo.gh

geometry.py	utility code for quaternions, copied from https://github.com/cmuphyscomp/hmv-s16
optirecv.py	RhinoPython support code for the Grasshopper patch

optirx.py	Optitrack multicast receiver and decoder, copied from https://github.com/cmuphyscomp/hmv-s16
LICENSE.txt	origin description and license for optirx.py

README.txt	this file
