#!/usr/bin/env python3

from math import floor
from random import random, shuffle
import time
from typing import Literal
# from typing_extensions import Literal
import keyboard
from keyboard._keyboard_event import KEY_DOWN
# import mido
import rtmidi
from dataclasses import dataclass

from scales import *
from utils import playTick

@dataclass
class RecordedMessage:
    time: int
    message: list[int]

DO_MIDI_OUTPUT = True
DO_SYNC_OUT = False
DO_MUTATE = False # Big changes
DO_TWEAK = False # Small changes

scale = BLUES
root_note = 70 #54
last_played_note = root_note
octave = -2 # negative or positive, relative to root note
notes_pressed: list[int] = []
all_notes_ever_played: list[int] = [] # useful to send a panic note off

sequence: list[RecordedMessage] = []
start_of_recording: float

arpeggio = [1, 1, 1, 7, 1, 1, 3, 5]
arpeggio = [1, None, None, 7, 2, 1, 3, 8]
current_arpeggio_index = 0
bpm = 120
notes_per_beat = 4
note_interval = 60 / bpm / notes_per_beat
note_duration_percentage = 0.2

cycle = 0
total_cycles = 4
macro_cycles = 2
note_index_to_change = 0
last_played_note_position_on_scale = 0
gravity_pull_of_the_root = 0.08

if DO_MIDI_OUTPUT:
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()
    midiout.open_port(0)
    print(available_ports)

mode: Literal['playing', 'will record', 'recording'] = 'playing'

# print(mido.get_output_names())

# midi_port = mido.open_output('SOUND')

def number_to_note(root: int, number: int):
    note = root + sum(scale) * octave
    for note_count in range(0, number - 1):
        note += scale[note_count % len(scale)]
    return note


def on_keyboard_event(event: keyboard.KeyboardEvent):
    global mode, sequence, start_of_recording, octave, root_note, last_played_note, scale, all_notes_ever_played
    is_key_down_event = event.event_type == KEY_DOWN

    print("[[[" + event.name + "]]]")

    # Panic
    if event.name == 'space':
        for note in all_notes_ever_played:
            print(note)
            time.sleep(0.01)
            DO_MIDI_OUTPUT and midiout.send_message([0x80, note, 0])
        all_notes_ever_played = []
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
    elif (event.name == '+' or event.name == '=') and octave < 4:
        octave += 1
    elif event.name == 'q':
        scale = WHOLE_TONE
    elif event.name == 'w':
        scale = MAJOR_SCALE
    elif event.name == 'e':
        scale = MINOR_SCALE
    elif event.name == 'r':
        scale = MELODIC_MINOR_SCALE
    elif event.name == 't':
        scale = HARMONIC_MINOR_SCALE
    elif event.name == 'y':
        scale = DIMINISHED
    elif event.name == 'u':
        scale = BLUES
    else:
        try:
            note = number_to_note(root_note, int(event.name))
            message: list[int] = None

            if is_key_down_event and not note in notes_pressed:
                # notes_pressed.append(note)
                # if not note in all_notes_ever_played:
                #     all_notes_ever_played.append(note)
                # channel 1, note, velocity
                # message = [0x90, note, 127]
                last_played_note = note
            elif not is_key_down_event and note in notes_pressed:
                # notes_pressed.remove(note)
                # message = [0x80, note, 0]
                pass

            if not message == None:
                DO_MIDI_OUTPUT and midiout.send_message(message)
                if mode == 'will record':
                        start_of_recording = time.time()
                        mode = 'recording'
                if mode == 'recording': 
                    sequence.append(RecordedMessage(time=time.time()-start_of_recording, message=message))
        
            # print(notes_pressed)
        except:
            pass

keyboard.hook(on_keyboard_event)

while True:
    index_to_use = current_arpeggio_index
    if DO_TWEAK and current_arpeggio_index == note_index_to_change and cycle%(total_cycles - 1) == 0:
        while arpeggio[index_to_use] == arpeggio[current_arpeggio_index]:
            index_to_use = floor(len(arpeggio) * random())
    note_in_arpeggio = arpeggio[index_to_use]

    DO_SYNC_OUT and playTick()

    if note_in_arpeggio != None:
        note = number_to_note(last_played_note, note_in_arpeggio)
        # print(note)
        DO_MIDI_OUTPUT and midiout.send_message([0x90, note, 127])

    time.sleep(note_interval - (note_interval * note_duration_percentage))

    if note_in_arpeggio != None:
        DO_MIDI_OUTPUT and midiout.send_message([0x80, note, 0])

    current_arpeggio_index += 1
    if current_arpeggio_index >= len(arpeggio):
        current_arpeggio_index = 0
        cycle += 1
        note_index_to_change = floor(len(arpeggio) * random())
        if DO_MUTATE and cycle%(total_cycles) == 0:
            shuffle(arpeggio)
        if DO_MUTATE and cycle%(total_cycles*macro_cycles) == 0:
            if random() < .5 - (gravity_pull_of_the_root * (root_note - last_played_note)):
                last_played_note_position_on_scale-=1
                last_played_note_position_on_scale = last_played_note_position_on_scale%len(scale)
                last_played_note -= scale[last_played_note_position_on_scale]
            else:
                # mod again just in case we're now in a scale with less notes
                last_played_note_position_on_scale = last_played_note_position_on_scale%len(scale)
                last_played_note += scale[last_played_note_position_on_scale]
                last_played_note_position_on_scale+=1
                last_played_note_position_on_scale = last_played_note_position_on_scale%len(scale)

    time.sleep(note_interval - (note_interval * (1 - note_duration_percentage)))
