#!/usr/bin/env python3

import mido
import pyautogui

# TODO: load a complete map from a file instead.
# There is a `pyautogui.KEYBOARD_KEYS` but there are too many (194 keys), gotta strip some of them.
KEY_MAP = {
    69: "space",
    70: "backspace",
}

def main():
    ports = mido.get_input_names()

    print("Available MIDI devices: ")
    for i, port in enumerate(ports):
        print(f"  {i}: {port}")

    idx = input("Select a device: ")
    try:
        device_name = ports[int(idx)]
        with mido.open_input(device_name) as port:
            print(f"successfully connected to '{port}'")
            for msg in port:
                # This is the left most key on my midi keyboard, allow it to act as `esc` key for now,
                # otherwise there is no way but to close the whole shell to stop the program
                # as `ctrl+c/z` are not working lol.
                if msg.note == 21:
                    break
                handle_note(msg.note, msg.type == "note_on")
                
    except IndexError as ie:
        raise ie
    except ValueError:
        print(f"input '{idx}' is not an integer")


def handle_note(note, pressed=True):
    related_key = KEY_MAP.get(note)
    
    if pressed:
        print("pressing:", note, ", simulating:", related_key)
        if related_key:
            pyautogui.keyDown(related_key)
    else:
        print("releasing", note, ", simulating:", related_key)
        if related_key:
            pyautogui.keyUp(related_key)

if __name__ == '__main__':
    main()
