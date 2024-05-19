#!/usr/bin/env python3

import rtmidi

def main():
    out = rtmidi.MidiOut()
    ports = out.get_ports()
    print(ports)


if __name__ == '__main__':
    main()
