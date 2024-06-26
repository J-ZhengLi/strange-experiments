#!/usr/bin/env python3

import time
import threading
from os import path

import pickle

import mido

from pynput import keyboard
from pynput.keyboard import Key, Controller, Listener, GlobalHotKeys, Events, KeyCode

kb = Controller()

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
            ans = input("do you want to run key mapping configuration now? (Y/n)").strip().lower()
            if ans.startswith("n"):
                print("cannot run without key configuration, aborting...")
                exit(1)
            elif ans.startswith("y") or not ans:
                key_map = key_remap(port)

                if key_map is not None:
                    # TODO: find a way to store this data in non-binary mode to support modification
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


class RemapEndException(Exception):
    def __init__(self, save=True):
        super().__init__()
        self.save = save


# God... I'm so bad at python...
# TODO: clean up this mess
def key_remap(port) -> dict | None:
    def finish(save: bool):
        global save_key_map
        global is_mapping
        save_key_map = save
        is_mapping = False

    def on_release(key):
        """
        Handle kb input.
        Returning `False` will stop the listener.
        """
        print("key({})".format(key))
        print(f"mapping key note: {mapping_for} to {key}")
        key_map[mapping_for] = key
        return False
    
    def on_meta_key_release(key):
        """
        Handle meta key (such as key combinations).
        """
        # FIXME: This function get called multiple times on pressed,
        # I don't know why! need to investigate.
        if key == KeyCode.from_char('\x13'):
            print("Configuration successful!")
            finish(True)
        elif key == KeyCode.from_char('\x11'):
            print("Configuration aborted, no key map will be stored.")
            finish(False)

    global save_key_map
    global is_mapping
    is_mapping = True
    save_key_map = False

    mapping_for = None
    # Prevent the `press a key on MIDI...` got printed twice
    print_key_prompt = True
    key_map = dict()
    
    print(
        "follow the instructions to remap keys,\n\
        press '<ctrl> + s' to save,\n\
        press '<ctrl> + q' to abort.\n"
    )

    try:
        while is_mapping:
            # Listen for meta key events at first
            meta_listener = keyboard.Listener(on_release=on_meta_key_release)
            meta_listener.start()

            if print_key_prompt:
                print("Press a key on MIDI device:", end=" ", flush=True)
            recv = port.receive()
            # only care when a key is released.
            if recv.type == "note_on":
                print_key_prompt = False
                continue
            else:
                print_key_prompt = True
            print("note({})".format(recv.note), end=". ", flush=True)
            mapping_for = recv.note

            print("Now pressing a key on keyboard:", end=" ", flush=True)
            # Listen to kb input for mapping
            with keyboard.Listener(on_release=on_release) as map_listener:
                map_listener.join()
    except Exception as e:
        print("unknown exception caught when mapping keys:", e)
    finally:
        if save_key_map:
            print(f"[Debug] Full keymap: {key_map}")
            return key_map
        else:
            return None


def handle_note(key_map: dict, note, pressed=True):
    related_key = key_map.get(note) if key_map is not None else None
    
    if pressed:
        print("pressing:", note, ", simulating:", related_key)
        if related_key:
            kb.press(related_key)
    else:
        print("releasing", note, ", simulating:", related_key)
        if related_key:
            kb.release(related_key)

if __name__ == '__main__':
    main()
