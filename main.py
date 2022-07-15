import struct
import typing as t
from enum import Enum, auto



class Key(Enum):
    up = auto()
    down = auto()
    left = auto()
    right = auto()
    shr = auto()
    shl = auto()
    a = auto()
    b = auto()
    x = auto()
    y = auto()
    select = auto()
    start = auto()


class Event(Enum):
    keydn = auto()
    keyup = auto()


class Device:
    def __init__(self):
        self.infile = open('/dev/input/by-id/usb-0079_USB_Gamepad-event-joystick', 'rb')
        self.arrow_down = None

    def __del__(self):
        self.infile.close()

    def _read_word(self) -> int:
        data = self.infile.read(4)
        (value,) = struct.unpack("<L", data)
        return value

    def _read_packet(self) -> t.Tuple[int, int, int, int, int, int]:
        word1 = self._read_word()
        word2 = self._read_word()
        word3 = self._read_word()
        word4 = self._read_word()
        word5 = self._read_word()
        word6 = self._read_word()
        return word1, word2, word3, word4, word5, word6

    def read(self) -> t.Tuple[Event, Key]:
        seq, zero, time, zero, key1, key2 = self._read_packet()

        is_arrow = key1 & 0x11 != 0

        seq, zero, time, zero, unknown, state = self._read_packet()

        if not is_arrow:
            self._read_packet()

        if is_arrow:
            keydown = key2 == 0xff or key2 == 0x00
        else:
            keydown = state == 1


        if is_arrow:
            is_updown = key1 & 0xffff0000 == 0x00010000
            is_upleft = key2 == 0x0
            key = {
                (True, True): Key.up,
                (True, False): Key.down,
                (False, True): Key.left,
                (False, False): Key.right,
            }[is_updown, is_upleft]
        else:
            key = {
                1: Key.x,
                2: Key.a,
                3: Key.b,
                4: Key.y,
                5: Key.shl,
                6: Key.shr,
                9: Key.select,
                10: Key.start,
            }[key2 & 0xf]

#        print(f'key1    = {key1:08x}')
#        print(f'key2    = {key2:08x}')
#        print(f'unknown = {unknown}')
#        print(f'state   = {state}')
#        print()
#        print(f'arrow?    {is_arrow}')
#        print(f'key     = {key}')
#        print(f'keydown?  {keydown}')
#        print(f'updown?   {is_updown}')
#        print(f'{word1:08x}  {word2:08x}  {word3:08x}  {word4:08x}  {word5:08x}  {word6:08x} ')
#        print("DONE")
#        print()

        if is_arrow and keydown:
            self.arrow_down = key

        if keydown:
            event = Event.keydn
        else:
            event = Event.keyup

        if event == Event.keyup and is_arrow:
            key = self.arrow_down
            self.arrow_down = None

        return event, key



def main():
    device = Device()
    while True:
        event, key = device.read()
        print(event, key)


if __name__ == '__main__':
    main()
