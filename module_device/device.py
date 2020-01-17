# 设备类
import datetime
import queue
import random
import threading
from time import sleep


class Device(object):
    # 当前时间
    current_time = None
    # 工作状态代号
    MODE_NORMAL = '01'
    MODE_INITING = '04'
    MODE_ENGINEER = '03'
    MODE_SNORING = '02'
    # 当前工作状态
    current_operating_mode = MODE_NORMAL

    # 当前固件版本
    current_version = '1.16a'
    # 设备ID
    ID = 'b00001'
    # 时间自增进程
    t_time_increase = False
    # 如果是止鼾模式   截至时间
    snore_time = None

    def __init__(self, queue_to_order: queue):
        self.queue_to_order = queue_to_order
        # 初始化线程
        # self.t_init = threading.Thread(target=self.set_operating_mode_normal)
        # 先设置设备为初始化状态
        self.current_operating_mode = self.MODE_INITING
        self.init()

    def set_operating_mode_normal(self):
        sleep(10)
        self.current_operating_mode = self.MODE_NORMAL
        print('设备初始化完成')
        # 发送消息
        self.queue_to_order.put(self.get_operating_mode())

    # 设置止鼾截止时间
    def set_snore_time(self, delay_time: int):
        # 根据current_time基础上延迟多少分钟
        # 如果当前时间为空，则获取系统时间
        if self.current_time is None:
            self.current_time = datetime.datetime.now()
        self.snore_time = self.current_time + datetime.timedelta(minutes=delay_time)

    # 获取止鼾截止时间
    def get_snore_time(self):
        return self.snore_time

    # 设置工作状态
    def set_operating_mode(self, mode: str, mins: int):
        # 设置工作状态
        self.current_operating_mode = mode
        # 工作状态是干预模式的话设置干预时间
        if mode == '02':
            self.set_snore_time(mins)

        # 如果设置工作状态为初始化模式  5s后发送工作状态切换为正常模式并且发送信息到手机
        if mode == self.MODE_INITING:
            self.init()
            # sleep(5)
            # self.current_operating_mode = self.MODE_NORMAL

    # 获取工作状态
    def get_operating_mode(self):
        return_str = str(self.current_operating_mode)

        if self.current_operating_mode == self.MODE_SNORING:
            # 如果设备当前时间为none 读取系统时间
            if self.current_time is None:
                self.current_time = datetime.datetime.now()
            # 如果打鼾干预截止时间为none 则为 随机取0-720时间 加上系统时间
            if self.snore_time is None:
                self.snore_time = self.current_time + datetime.timedelta(minutes=random.randint[0, 720])

            # 剩余打鼾时间 = 打鼾截至时间 - 当前设备时间的分钟数
            last_time = self.snore_time - self.current_time
            # 剩余打鼾干预分钟 16 进制字符串
            last_time_minutes_hex = hex(int(last_time.total_seconds() / 60))[2:]

            while len(last_time_minutes_hex) < 4:
                last_time_minutes_hex = "0" + last_time_minutes_hex
            return_str += last_time_minutes_hex
        else:
            return_str += "0000"

        return return_str

    # 获取设备信息
    def get_device_info(self):
        """
        获取设备信息
        :return: ID  b00001 (3字节)
                Ver 1.16a（4字节）ASCII码
                Ver 1.1a(3字节)
                Ver 1.1(2字节)
                例：
                    0xB00001 31313661
                    设备id为b00001
                    固件版本号为 1.16a
        """

        re_cv = ""
        cv = self.current_version
        # 去掉点
        cv = cv.replace(".", "")
        # 转为ASCII码
        for c in cv:
            # print(hex(ord(c))[2:])
            re_cv += hex(ord(c))[2:]

        return self.ID + re_cv

    # 设置时间
    def set_time(self, phone_time: str):
        """
                设置时间
        :param phone_time: 手机时间
        :return: none

        """

        if not self.t_time_increase:
            self.t_time_increase = threading.Thread(target=self.time_flu, args=())
            self.t_time_increase.start()
            self.t_time_increase.join()
        # 字符串转datetime
        dt = datetime.datetime.strptime(phone_time, '%Y%m%d%H%M')
        self.current_time = dt

    def time_flu(self):
        self.t_time_increase = True
        while True:
            # 60秒后，当前时间增加一分钟
            sleep(60)
            self.current_time += datetime.timedelta(minutes=1)

    def init(self):
        self.t_init = threading.Thread(target=self.set_operating_mode_normal)
        self.t_init.setDaemon(True)
        self.t_init.start()
