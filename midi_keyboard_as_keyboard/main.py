#!/usr/bin/env python3

"""
TODO: Now that the midi keyboard can be successfully connected,
find out how to emulate keyboard pressing next
"""

import mido

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
                print("message:", msg)
    except IndexError as ie:
        raise ie
    except ValueError:
        print(f"input '{idx}' is not an integer")


if __name__ == '__main__':
    main()
