import datetime
import random

if __name__ == '__main__':
    # t = datetime.datetime.now()
    #
    # delay_time = t + datetime.timedelta(minutes=90)
    #
    # format_time = delay_time.strftime('%Y%m%d%H%M%S')
    #
    # s = (str(1), format_time)
    #
    # send_str = " ".join(s)
    # print(send_str)

    # l = '1'.split(" ")
    # print(l)
    # print(len(l))
    # var = hex(1)[2:]
    # while len(var) < 4:
    #     var = "0" + var
    #
    # print(var)

    t1 = datetime.datetime.now()
    t2 = t1 + datetime.timedelta(minutes=20)

    last_t = t2 - t1

    t_minutes = hex(int(last_t.total_seconds() / 60))[2:]

    while len(t_minutes) < 4:
        t_minutes = "0" + t_minutes

    print(t_minutes)
