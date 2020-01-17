import queue
import threading


class MessageManager(object):
    def __init__(self, queue_to_order: queue, queue_from_order: queue, queue_to_comm: queue, queue_from_comm: queue,
                 pool):
        # 启动线程接收通讯模块传来的消息
        self.queue_to_order = queue_to_order
        self.queue_from_order = queue_from_order
        self.queue_to_comm = queue_to_comm
        self.queue_from_comm = queue_from_comm
        self.pool = pool

    def ready(self):
        t_recv = threading.Thread(target=self.unpacking, args=())
        self.pool.append(t_recv)
        t_to_comm = threading.Thread(target=self.to_comm, args=())
        self.pool.append(t_to_comm)

    def to_comm(self):
        while True:
            # 监听命令模块发送来的数据
            info = self.queue_from_order.get(block=True, timeout=None)
            # print('命令模块发送:%s' % info)
            send_str = self.packing(info[0], info[1])
            self.queue_to_comm.put(send_str)

    def get_byte_data(self, byte_len=1):
        """
        get one byte from queue
        :param byte_len: num of bytes
        :return: bytes
        """
        data = ""
        # get data from queue
        for _ in range(byte_len * 2):
            data += self.queue_from_comm.get(block=True, timeout=None)
        # return the data by one byte
        return data

    def packing(self, send_order, send_data):
        data_len = (len(send_order) + len(send_data)) // 2

        data_len_byte = self.int_2_bytes(data_len)
        # add
        CRC_int = (data_len + int(send_data, 16)) & 0xff
        # print('%s + %s(%s) = %s' % (data_len, int(send_data, 16), send_data, CRC_int))
        CRC_str = self.int_2_bytes(CRC_int)
        return "AA" + data_len_byte + send_order + send_data + CRC_str + "BB"

    def int_2_bytes(self, i: int, byte_num=1):
        i_hex = hex(i).replace('0x', "")
        return ("00" + i_hex)[-(2 * byte_num):]

    # unpacking
    def unpacking(self):
        """
        unpacking the package
        解包
        :return:
        """
        while True:
            # get the data by one byte
            package_start = self.get_byte_data()
            # print("package_start :%s" % package_start)
            # check byte is "AA" or not
            if package_start == 'AA':
                # get one byte cast to int mean data_length
                data_length = int(self.get_byte_data(), 16)
                # print("data_length : %s" % data_length)
                # get package data part
                data = self.get_byte_data(byte_len=data_length)
                # print("data : %s" % data)
                # get other one byte is CRC
                CRC = int(self.get_byte_data(), 16)
                # print("CRC : %s" % CRC)
                package_end = self.get_byte_data()
                # print("package_end : %s" % package_end)
                if package_end == 'BB':
                    # CRC check
                    # get data`s last byte
                    data_low = int(data[-2:], 16)
                    # print("data_low : %s" % data_low)
                    if CRC == (data_low + data_length) % 256:
                        # self.order_analysis(data)
                        self.queue_to_order.put(data)
