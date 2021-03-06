import random
import string
import time, hashlib
import uuid

import datetime


def timedemo():
    s = time.time().__str__()
    print('时间戳：%s' % s)
    s1 = "sy"
    s2 = ''.join(random.sample(string.digits + string.ascii_letters, 8))
    s3 = s1 + s + s2
    print(s3)
    str = uuid.uuid3(uuid.NAMESPACE_DNS, s3)
    print(str.__str__().__len__())
    print(str.__str__())


def datetimedemo():
    d1 = datetime.datetime.now()
    print(type(d1))
    print(d1)

    s = time.time().__str__()
    print('时间戳：%s' % s)


if __name__ == '__main__':
    # timedemo()
    # datetimedemo()
    # f = (2 + 4)//2
    # print(f.hex())
    # print(hex(f))

    # f_hex = hex(f)
    # print(("00" + f_hex.replace('0x', ""))[-2:])
    # for i in range(0, 100):
    #     print(''.join([random.choice("0123456789ABCDEF") for _ in range(6)])

    d1 = datetime.datetime.now().date()
    print(d1)

    date_str = "20191231"
    date = datetime.datetime.strptime(date_str, "%Y%m%d").date()
    print(date)

    if date >= d1:
        print('大于等于')
    else:
        print('小于')
