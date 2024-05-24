#!/usr/bin/env python3

from os import path
import pickle

import mido
from pynput.keyboard import Key, Controller

keyboard = Controller()

def main():
    ports = mido.get_input_names()

    print("Available MIDI devices: ")
    for i, port in enumerate(ports):
        print(f"  {i}: {port}")

    sel = input("Select a device: ")
    try:
        idx = 0 if not sel else int(sel)
        device_name = ports[idx]
        key_map = get_key_map()
        with mido.open_input(device_name) as port:
            print(f"successfully connected to '{port}'")
            for msg in port:
                # This is the left most key on my midi keyboard, allow it to act as `esc` key for now,
                # otherwise there is no way but to close the whole shell to stop the program
                # as `ctrl+c/z` are not working lol.
                if msg.note == 21:
                    break
                handle_note(key_map, msg.note, msg.type == "note_on")
    except IndexError as ie:
        raise ie
    except ValueError as ve:
        print(f"invalid choice of device '{sel}': {ve}")
        exit(1)
    except Exception as uncaught:
        print("yo what's going on?", uncaught)
        exit(1)


def get_key_map() -> dict:
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
                # TODO (running out of time, need to sleep, gotta work tomorrow... sad): replace this with the actual wizard
                key_map = {
                    69: Key.space,
                    70: Key.backspace,
                    71: "a",
                }
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
