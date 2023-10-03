#!/usr/bin/env python3

import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
midiout.open_port(0)
print(available_ports)