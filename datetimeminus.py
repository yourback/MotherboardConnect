import datetime
from time import sleep

if __name__ == '__main__':
    TENS = 10

    time1 = datetime.datetime.now()
    sleep(10)
    time2 = datetime.datetime.now()
    print(time1)
    print(time2)

    time3 = time2 - time1

    print(time3.seconds == 10)

    print(time3.days)
