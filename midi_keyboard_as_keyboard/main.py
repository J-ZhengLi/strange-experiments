#!/usr/bin/env python3

import time
from os import path
from enum import Enum

import pickle

import mido
from pynput.keyboard import Key, Controller, HotKey, Listener, GlobalHotKeys

class State(Enum):
    PLAYING = 1
    MAPPING = 2
    IDLE = 3

keyboard = Controller()
global_state = State.IDLE

def main():
    ports = mido.get_input_names()

    if not ports:
        print("waiting for MIDI device...")
        while not ports:
            time.sleep(1)
            ports = mido.get_input_names()
    
    try:
        index = 0
        if len(ports) > 1:
            print("Available MIDI devices: ")
            for i, port in enumerate(ports):
                print(f"  {i}: {port}")
            index = int(input("Select a device: "))

        # Already checked that `ports` is not empty, so this should be fine
        device_name = ports[index]

        with mido.open_input(device_name) as port:
            print("successfully connected to '{}'".format(port.name))

            key_map = get_key_map(port)

            update_state(State.PLAYING)
            for msg in port:
                handle_note(key_map, msg.note, msg.type == "note_on")
    except IndexError as ie:
        raise ie
    except ValueError as ve:
        print(f"invalid choice of device '{index}': {ve}")
        exit(1)
    except KeyboardInterrupt:
        # FIXME: rather than requiring another key pressing, find a way to exit immediately
        exit(0)
    except Exception as uncaught:
        print("yo what's going on?", uncaught)
        exit(1)


def get_key_map(port) -> dict:
    """ Try to read key map file, if it doesn't exist, start key mapping wizard. """

    script_dir = path.dirname(path.realpath(__file__))
    key_map_filepath = path.join(script_dir, "key-mapping")

    try:
        if path.isfile(key_map_filepath):
            key_map = dict()
            with open(key_map_filepath, "rb") as key_map_file:
                key_map = pickle.load(key_map_file)
            print("key mapping loaded:", key_map)
            return key_map
        else:
            # key mapping wizard
            print("It looks like you are running this application for the first time,")
            ans = input("do you want to run key mapping configuration now? (y/N)").strip().lower()
            if ans.startswith("n") or not ans:
                print("cannot run without key configuration, aborting...")
                exit(1)
            elif ans.startswith("y"):
                key_map = key_remap(port)

                with open(key_map_filepath, "wb") as key_map_file:
                    pickle.dump(key_map, key_map_file)
                return key_map
            else:
                print(f"invalid option '{ans}'")
                exit(1)
    except ValueError as ve:
        print("failed to get key map:", ve)
        exit(1)
    except Exception as ex:
        raise ex


def update_state(new_state: State):
    global global_state
    global_state = new_state


def key_remap(port) -> dict:
    def on_save():
        update_state(State.IDLE)
    
    def on_abort():
        key_map = dict()
        update_state(State.IDLE)

    update_state(State.MAPPING)

    key_map = dict()
    
    # Register hotkeys
    # with GlobalHotKeys({"<ctrl>+s": on_save, "<ctrl>+q": on_abort}) as hotkeys:
    #     hotkeys.join()
    print(
        "follow the instructions to remap keys,\n\
        press '<ctrl> + s' to save,\n\
        press '<ctrl> + q' to abort.\n"
    )

    while global_state is State.MAPPING:
        print("press a key on MIDI device:", end=" ")

        recv = port.receive()
        print("note({})".format(recv.note))

        # TODO: Handle keyboard event.
        print("now press a key on keyboard:", end="")
        update_state(State.IDLE)

    return key_map


def handle_note(key_map: dict, note, pressed=True):
    related_key = key_map.get(note)
    
    if pressed:
        print("pressing:", note, ", simulating:", related_key)
        if related_key:
            keyboard.press(related_key)
    else:
        print("releasing", note, ", simulating:", related_key)
        if related_key:
            keyboard.release(related_key)

if __name__ == '__main__':
    main()
