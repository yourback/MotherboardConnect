import binascii
import queue
import threading
import time

import serial  # 导入模块


# 消息接收与发送


# 是否开启了接口
def is_opened(func):
    def is_opened_inner(s, send_order, send_data):
        if not s.ser.isOpen():
            s.open()

        func(s, send_order, send_data)

    return is_opened_inner


# 串口连接类
class PortManager(object):
    current_device = None

    # queue
    read_queue = queue.Queue(maxsize=-1)

    # 包序列
    num = 0

    # # 16进制字符串  奇偶验证   返回 0 / 1    偶/奇
    # def get_check_result(self, hex_string: str) -> int:
    #     check_result_int = 0
    #     for s in hex_string:
    #         current_result = 0
    #         i = int(s, 16)
    #         #  位运算
    #         for j in range(4):
    #             v = i >> j & 1
    #             current_result += v
    #         check_result_int += current_result
    #     return check_result_int % 2

    def __init__(self, com_num: str, queue_out: queue, queue_in: queue, pool: list):
        # 线程池
        self.pool = pool
        # 发送到消息处理模块的线路
        self.read_queue = queue_out
        # 接收消息处理模块发来消息的线路
        self.queue_in = queue_in
        # 端口初始化
        self.ser = serial.Serial(com_num, 1000000, timeout=0.5)  # 新建ser接口后续通讯使用

    # 开始接收消息
    def ready(self):
        t_recv = threading.Thread(target=self.start_recv, args=())
        self.pool.append(t_recv)
        t_send = threading.Thread(target=self.start_send, args=())
        self.pool.append(t_send)

    # 打开接口并开始接收
    def open(self):
        if not self.ser.isOpen():
            self.ser.open()
        return self

        # if self.current_device is None:
        #     self.current_device = Device()
        # 接收数据
        # t_recv = threading.Thread(target=self.start_recv, args=())
        # t_detail = threading.Thread(target=self.unpacking, args=())
        # t_detail.start()
        # t_recv.start()
        # t_detail.join()
        # t_recv.join()
        # print('接收')
        # print(self.ser.readline())
        # print('接收完毕')

    def close(self):
        self.ser.close()

    # 开始接收数据
    def start_recv(self):
        """
        start recv data from BLE
        :return:
        """
        print("等待接收数据中....")
        while True:
            time.sleep(0.5)

            count = self.ser.inWaiting()
            if count > 0:
                return_str = self.ser.read(count)
                if return_str == b'connected':
                    print("设备已经连接")
                elif return_str == b'disconnected':
                    print('设备主动断开连接')
                else:
                    # put data into queue
                    var = str(binascii.b2a_hex(return_str))[2:-1].upper()
                    # print("var:%s" % var)
                    for s in list(var):
                        self.read_queue.put(s)

    # 开始发送数据
    def start_send(self):
        while True:
            info = self.queue_in.get(block=True, timeout=None)
            self.send(info)

    # @is_opened
    def send(self, ssr: str):
        self.ser.write(bytes.fromhex(ssr))
