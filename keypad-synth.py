#!/usr/bin/env python3

import time
from typing import Literal
import keyboard
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
# import mido
import rtmidi
from dataclasses import dataclass

from scales import *

@dataclass
class RecordedMessage:
    time: int
    message: list[int]

MIDI_OUTPUT = True

scale = BLUES
root_note = 54
octave = -2 # negative or positive, relative to root note
notesPressed: list[int] = []
allNotesEverPlayed: list[int] = [] # useful to send a panic note off

sequence: list[RecordedMessage] = []
startOfRecording: float

if MIDI_OUTPUT:
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()
    midiout.open_port(0)
    print(available_ports)

mode: Literal['playing', 'will record', 'recording'] = 'playing'

# print(mido.get_output_names())

# midi_port = mido.open_output('SOUND')

def number_to_note(number: int):
    note = root_note + sum(scale) * octave
    for note_count in range(0, number - 1):
        note += scale[note_count % len(scale)]
    return note


def on_keyboard_event(event: keyboard.KeyboardEvent):
    global mode, sequence, startOfRecording, octave
    is_key_down_event = event.event_type == KEY_DOWN

    print("[[[" + event.name + "]]]")

    # Panic
    if event.name == 'space':
        for note in allNotesEverPlayed:
            print(note)
            time.sleep(0.01)
            MIDI_OUTPUT and midiout.send_message([0x80, note, 0])
        allNotesEverPlayed = []
    elif event.name == '0':
        # TODO: set play head to start

        if mode == 'playing':
            sequence = []
            mode = 'will record'
        elif mode == 'will record':
            sequence = []
            mode = 'playing'
        elif mode == 'recording':
            mode = 'playing'
    elif event.name == '-' and octave > -4:
        octave -= 1
    elif event.name == '+' and octave < 4:
        octave += 1
    else:
        try:
            note = number_to_note(int(event.name))
            message: list[int] = None

            if is_key_down_event and not note in notesPressed:
                notesPressed.append(note)
                if not note in allNotesEverPlayed:
                    allNotesEverPlayed.append(note)
                # channel 1, note, velocity
                message = [0x90, note, 127]
            elif not is_key_down_event and note in notesPressed:
                notesPressed.remove(note)
                message = [0x80, note, 0]

            if not message == None:
                MIDI_OUTPUT and midiout.send_message(message)
                if mode == 'will record':
                        startOfRecording = time.time()
                        mode = 'recording'
                if mode == 'recording': 
                    sequence.append(RecordedMessage(time=time.time()-startOfRecording, message=message))
        
            print(notesPressed)
        except:
            pass

keyboard.hook(lambda e: on_keyboard_event(e))

while True:
    # user_input = input("Number: ")
    # numeric_input = int(user_input)
    # note = number_to_note(numeric_input)
    
    
    # print(note)

    time.sleep(0.5)
