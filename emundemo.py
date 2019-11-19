from enum import Enum


class Animals(Enum):
    INFO = "1F"


if __name__ == '__main__':
    # print(Animals.INFO.value)
    ts = '116a'
    for t in ts:
        print(t)
        print(hex(ord(t))[2:])
