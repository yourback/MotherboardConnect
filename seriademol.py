import binascii
import datetime
import random
import threading
import time
from enum import Enum
from queue import Queue
from time import sleep
import queue
from typing import Any

import serial  # 导入模块


# 接口orders枚举类
# 初始化
class OrderPortEnum(Enum):
    # --------------- 设置工作状态功能 ------------------
    # 接收设置设备工作状态命令
    RECV_SET_DEVICE_WORK_MODE = '01'
    # 发送设置设备工作状态结果
    RETURN_SET_DEVICE_WORK_MODE = '02'

    # --------------- 获得工作状态功能 ------------------
    # 接收获取设备工作状态命令
    RECV_GET_DEVICE_WORK_MODE = '03'
    # 发送 当前设备工作状态
    RETURN_GET_DEVICE_WORK_MODE = '04'

    # --------------- 读取传感器信息功能 ------------------
    # 接收读取传感器信息
    RECV_GET_DEVICE_SENSOR_INFO = '05'
    # 发送读取传感器信息
    RETURN_GET_DEVICE_SENSOR_INFO = '06'

    # --------------- 读取电机状态功能 ------------------
    # 接收 读取各电机状态信息
    RECV_GET_DEVICE_MOTOR_INFO = '07'
    # 返回 读取各电机状态信息
    RETURN_GET_DEVICE_MOTOR_INFO = '08'

    # --------------- 设置电机运转功能 ------------------
    # 接收 设置某个电机开始工作
    RECV_SET_DEVICE_MOTOR_RUN = '09'
    # 返回 设置某个电机开始工作
    RETURN_SET_DEVICE_MOTOR_RUN = '0A'

    # --------------- 设置电机停止功能 ------------------
    # 接收 设置某个电机停止工作
    RECV_SET_DEVICE_MOTOR_STOP_RUN = '0B'
    # 返回 设置电机停止工作成功 失败
    RETURN_SET_DEVICE_MOTOR_STOP_RUN = '0C'

    # --------------- 设置开发板时间功能 ------------------
    # 接收 设置当前时间（对表）
    RECV_SET_DEVICE_TIME = '0D'
    # 返回 设置时间成功
    RETURN_SET_DEVICE_TIME = '0E'

    # --------------- send file to phone ------------------
    # 接收 start send file func
    RECV_START_SEND_FILE = '0F'
    # 返回 file package num
    RETURN_PACKAGE_NUM = '10'
    # 接收 phone request someone package
    RECV_PHONE_REQUEST_SOMEONE_PACKAGE = '11'
    # 返回 send file package
    RETURN_SEND_PACKAGE = '12'

    # --------------- 升级功能 ------------------
    # 接收 开启升级功能 命令 contain num of package
    RECV_UPDATE = '13'
    # 发送 已经准备好接收升级文件
    RETURN_READY_RECV_UPDATE_FILE = '14'
    # 接收 package info
    RECV_PACKAGE = '15'
    # 发送 package ok
    RETURN_PACKAGE_OK = '16'
    # 发送 升级完成（暂时用不到）
    RETURN_UPDATE_FINISHED = '17'

    # --------------- 同步主控板数据到手机端功能 ------------------
    # 接收 同步主控板数据到手机端
    RECV_SYNC_DATA = '18'
    # 发送 相关数据
    RETURN_SYNC_DATA = '19'
    # 接收 num of package
    RECV_PACKAGE_NUM = '1A'
    # send num of package
    RETURN_PACKAGE_DATA = '1B'

    # --------------- 获得设备id和固件版本号功能 ------------------
    # 接收获取设备信息  id和版本号
    RECV_DEVICE_INFO = '1C'
    # 发送设备信息  id和版本号
    RETURN_DEVICE_INFO = '1D'

    # --------------- 工程师模式下启动止鼾功能 ------------------
    # 接收 工程师模式下启动止鼾
    RECV_ENGINEER_START_NO_SNORE = '1E'
    # 发送 工程师模式下启动止鼾结果
    RETURN_ENGINEER_START_NO_SNORE = '1F'

    # --------------- 工程师模式下停止止鼾功能 ------------------
    # 接收 工程师模式下停止止鼾
    RECV_ENGINEER_STOP_NO_SNORE = '20'
    # 发送 工程师模式下停止止鼾结果
    RETURN_ENGINEER_STOP_NO_SNORE = '21'

    # --------------- 工程师模式下获取 是否有鼾声，是否触发限位功能 ------------------
    # 接收 工程师模式下获取 是否有鼾声，
    RECV_ENGINEER_SNORE = '22'
    # 发送 工程师模式下获取 是否有鼾声
    RETURN_ENGINEER_SNORE = '23'

    # --------------- 工程师模式下获取 杆头压力传感器数据 功能 ------------------
    # 接收 工程师模式下获取 杆头压力传感器数据 命令
    RECV_ENGINEER_MOTOR_PRESS = '24'
    # 发送 工程师模式下获取 杆头压力传感器数据
    RETURN_ENGINEER_MOTOR_PRESS = '25'

    # --------------- 工程师模式下获取 肩部压力传感器数据 功能 ------------------
    # 接收 工程师模式下获取 肩部压力传感器数据 命令
    RECV_ENGINEER_SHOULDER_PRESS = '26'
    # 发送 工程师模式下获取 肩部压力传感器数据
    RETURN_ENGINEER_SHOULDER_PRESS = '27'

    # --------------- 工程师模式下获取 是否有鼾声，是否触发限位功能 ------------------
    # 接收 工程师模式下获取 是否触发限位 命令
    RECV_ENGINEER_LIMIT = '28'
    # 发送 工程师模式下获取 是否触发限位
    RETURN_ENGINEER_LIMIT = '29'


# 设备类
class Device(object):
    # 当前时间
    current_time = None
    # 当前工作状态
    current_operating_mode = '01'
    # 当前固件版本
    current_version = '1.16a'
    # 设备ID
    ID = 'b00001'
    # 时间自增进程
    t_time_increase = False
    # 如果是止鼾模式   截至时间
    snore_time = None

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

    # 获取工作状态
    def get_operating_mode(self):
        return_str = str(self.current_operating_mode)

        if self.current_operating_mode == '02':
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
        sleep(5)
        i = random.choice([0, 1])
        return i


# 是否开启了接口
def is_opened(func):
    def is_opened_inner(s, send_order, send_data):
        if not s.ser.isOpen():
            s.open()

        func(s, send_order, send_data)

    return is_opened_inner


class ComConnected(object):
    current_device = None

    # queue
    read_queue = queue.Queue(maxsize=-1)

    # 包序列
    num = 0

    # 16进制字符串  奇偶验证   返回 0 / 1    偶/奇
    def get_check_result(self, hex_string: str) -> int:
        check_result_int = 0
        for s in hex_string:
            current_result = 0
            i = int(s, 16)
            #  位运算
            for j in range(4):
                v = i >> j & 1
                current_result += v
            check_result_int += current_result
        return check_result_int % 2

    def __init__(self, com_num: str):
        self.ser = serial.Serial(com_num, 1000000, timeout=0.5)  # 新建ser接口后续通讯使用
        self.open()

    # 打开接口并开始接收
    def open(self):
        if not self.ser.isOpen():
            self.ser.open()

        if self.current_device is None:
            self.current_device = Device()
        # 接收数据
        t_recv = threading.Thread(target=self.start_recv, args=())
        t_detail = threading.Thread(target=self.unpacking, args=())
        t_detail.start()
        t_recv.start()
        t_detail.join()
        t_recv.join()
        # print('接收')
        # print(self.ser.readline())
        # print('接收完毕')

    def close(self):
        self.ser.close()

    def int_2_bytes(self, i: int, byte_num=1):
        i_hex = hex(i).replace('0x', "")
        return ("00" + i_hex)[-(2 * byte_num):]

    @is_opened
    def send(self, send_order: str, send_data: str):
        data_len = (len(send_order) + len(send_data)) // 2
        # print("datalen:%s" % data_len)

        data_len_byte = self.int_2_bytes(data_len)
        # add
        CRC_int = (data_len + int(send_data, 16)) & 0xff
        CRC_str = self.int_2_bytes(CRC_int)
        ssr = "AA" + data_len_byte + send_order + send_data + CRC_str + "BB"
        # print("发送数据：%s" % ssr)
        self.ser.write(bytes.fromhex(ssr))

    def get_byte_data(self, byte_len=1):
        """
        get one byte from queue
        :param byte_len: num of bytes
        :return: bytes
        """
        data = ""
        # get data from queue
        for _ in range(byte_len * 2):
            data += self.read_queue.get(block=True, timeout=None)
        # return the data by one byte
        return data

    # unpacking
    def unpacking(self):
        """
        unpacking the package
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
                        self.order_analysis(data)

    # 开始接收数据
    def start_recv(self):
        """
        start recv data from BLE
        :return:
        """
        print("等待接收数据中....")
        while True:
            # return_str = self.ser.readline().decode("utf8")
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
                #
                #
                #     print('接收到数据:%s' % var)
                #     # 如果不是AA开始，BB结束提示信息错误
                #     if not (var.startswith("AA") and var.endswith("BB")):
                #         print('无效指令，不做回应')
                #     else:
                #         try:
                #             # 接口实现
                #             # AABB删除
                #             rs = var.replace("AA", "").replace("BB", "")
                #             # 包序列
                #             rs_num = rs[0:2]
                #             print('包序列：' + rs_num)
                #             # 命令
                #             rs_order = rs[2:4]
                #             print('命令：' + rs_order)
                #
                #             rs_data = rs[4:-2]
                #             rs_check = rs[-2:]
                #
                #             print('数据：' + rs_data)
                #             print('验证：' + rs_check)
                #             # AA030103000000030001BB
                #             # AA030103000000030001BB
                #
                #             if rs_order == OrderPortEnum.RECV_SET_DEVICE_WORK_MODE.value:
                #                 # 设置设备工作状态
                #                 print("order:设置设备工作状态")
                #                 mode_str = rs_data[:2]
                #                 mins_int = int(rs_data[2:], 16)
                #                 self.current_device.set_operating_mode(mode_str, mins_int)
                #                 # 返回的命令与order
                #                 send_order = OrderPortEnum.RETURN_SET_DEVICE_WORK_MODE.value
                #                 send_data = '00'
                #
                #             elif rs_order == OrderPortEnum.RECV_GET_DEVICE_WORK_MODE.value:
                #                 # 获取设备工作状态
                #                 print("order:获取设备工作状态")
                #                 send_order = OrderPortEnum.RETURN_GET_DEVICE_WORK_MODE.value
                #                 # 获取设备工作状态
                #                 send_data = self.current_device.get_operating_mode()
                #
                #             elif rs_order == OrderPortEnum.RECV_GET_DEVICE_SENSOR_INFO.value:
                #                 # 读取传感器信息功能
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_GET_DEVICE_MOTOR_INFO.value:
                #                 # 读取各电机状态信息
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_SET_DEVICE_MOTOR_RUN.value:
                #                 # 设置某个电机开始工作
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_SET_DEVICE_MOTOR_STOP_RUN.value:
                #                 # 设置某个电机停止工作
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_SET_DEVICE_TIME.value:
                #                 # 设置开发板时间功能
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_START_RECORDING.value:
                #                 # 开启录音功能
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_READY_RECV_RECORDING_FILE.value:
                #                 # 手机已经准备好接收录音文件
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_READY_RECV_RECORDING_FILE_OK.value:
                #                 # 手机端接收录音文件完成/错误
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_UPDATE.value:
                #                 # 开启升级功能
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_UPDATE_FILE.value:
                #                 # 手机端传送升级文件
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_UPDATE_FILE_FINISHED.value:
                #                 # 手机端传送升级文件完成
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_SYNC_DATA.value:
                #                 # 同步主控板数据到手机端
                #                 pass
                #             elif rs_order == OrderPortEnum.RECV_SYNC_DATA_OK.value:
                #                 # 手机收到数据
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_DEVICE_INFO.value:
                #                 # 接收获取设备信息  id和版本号
                #                 print('order:接收获取设备信息  id和版本号')
                #                 send_data = self.current_device.get_device_info()
                #                 send_order = OrderPortEnum.RETURN_DEVICE_INFO.value
                #
                #             elif rs_order == OrderPortEnum.RECV_ENGINEER_START_NO_SNORE.value:
                #                 # 工程师模式下启动止鼾
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_ENGINEER_STOP_NO_SNORE.value:
                #                 # 工程师模式下停止止鼾
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_ENGINEER_SNORE.value:
                #                 # 工程师模式下获取 是否有鼾声，
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_ENGINEER_MOTOR_PRESS.value:
                #                 # 接收 工程师模式下获取 杆头压力传感器数据 命令
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_ENGINEER_SHOULDER_PRESS.value:
                #                 # 接收 工程师模式下获取 肩部压力传感器数据 命令
                #                 pass
                #
                #             elif rs_order == OrderPortEnum.RECV_ENGINEER_LIMIT.value:
                #                 # 接收 工程师模式下获取 是否触发限位功能 命令
                #                 pass
                #
                #         except Exception as e:
                #             print("指令解析出错：" + e.__str__())
                #             print('无效指令，不做回应')
                #
                # if send_order:
                #     print('send_order:%s' % send_order)
                #     print('send_data:%s' % send_data)
                #     self.send(send_order=send_order, send_data=send_data)

    f_w = None

    def order_analysis(self, data):
        """
        order analysis order
        :return:
        """
        rs_order = data[:2]
        rs_message = data[2:]

        # print("rs_order ：%s" % rs_order)
        # print("rs_message ：%s" % rs_message)

        response_order = ''
        response_message = ''

        # 升级文件总包数
        package_num = 0

        if rs_order == OrderPortEnum.RECV_SET_DEVICE_WORK_MODE.value:
            # 设置设备工作状态
            print("order:设置设备工作状态")
            mode_str = rs_message[:2]
            mins_int = int(rs_message[2:], 16)
            self.current_device.set_operating_mode(mode_str, mins_int)
            # 返回的命令与order
            response_order = OrderPortEnum.RETURN_SET_DEVICE_WORK_MODE.value
            response_message = '00'

        elif rs_order == OrderPortEnum.RECV_GET_DEVICE_WORK_MODE.value:
            # 获取设备工作状态
            print("order:获取设备工作状态")
            response_order = OrderPortEnum.RETURN_GET_DEVICE_WORK_MODE.value
            # 获取设备工作状态
            response_message = self.current_device.get_operating_mode()

        elif rs_order == OrderPortEnum.RECV_GET_DEVICE_SENSOR_INFO.value:
            # 读取传感器信息功能
            pass
        elif rs_order == OrderPortEnum.RECV_GET_DEVICE_MOTOR_INFO.value:
            # 读取各电机状态信息
            pass
        elif rs_order == OrderPortEnum.RECV_SET_DEVICE_MOTOR_RUN.value:
            # 设置某个电机开始工作
            pass
        elif rs_order == OrderPortEnum.RECV_SET_DEVICE_MOTOR_STOP_RUN.value:
            # 设置某个电机停止工作
            pass
        elif rs_order == OrderPortEnum.RECV_SET_DEVICE_TIME.value:
            # 设置开发板时间功能
            pass

        elif rs_order == OrderPortEnum.RECV_START_SEND_FILE.value:
            # 开启录音功能
            pass
        elif rs_order == OrderPortEnum.RECV_PHONE_REQUEST_SOMEONE_PACKAGE.value:
            # 手机已经准备好接收录音文件
            pass

        elif rs_order == OrderPortEnum.RECV_UPDATE.value:
            # 开启升级功能
            print("开启固件升级功能,总包数:%s" % int(rs_message, 16))
            package_num = int(rs_message, 16)
            response_order = OrderPortEnum.RETURN_READY_RECV_UPDATE_FILE.value
            response_message = rs_message
        elif rs_order == OrderPortEnum.RECV_PACKAGE.value:
            # 手机端传送升级文件（分包）
            # 新建升级文件
            if self.f_w is None:
                print('文件为空，打开文件')
                self.f_w = open('firmware/firmware_update.zip', 'wb')

            recv_package_hex = rs_message[:4]
            recv_package_int = int(recv_package_hex, 16)
            recv_package_content = rs_message[4:]
            print('手机传送升级文件中...当前包:%s' % recv_package_int)
            print('文件内容：%s' % recv_package_content)

            # 写文件位置
            write_position = 43 * (recv_package_int - 1)
            # 移动写文件指针
            self.f_w.seek(write_position)
            # 写文件
            self.f_w.write(bytes.fromhex(recv_package_content))
            # 如果文件是最后一包关闭文件
            if package_num == recv_package_int:
                print('传输完毕，关闭文件')
                self.f_w.close()
                self.f_w = None

            # 返回
            response_order = OrderPortEnum.RETURN_PACKAGE_OK.value
            response_message = recv_package_hex
        elif rs_order == OrderPortEnum.RECV_SYNC_DATA.value:
            # 同步主控板数据到手机端
            pass
        elif rs_order == OrderPortEnum.RECV_PACKAGE_NUM.value:
            # 手机收到数据
            pass

        elif rs_order == OrderPortEnum.RECV_DEVICE_INFO.value:
            # 接收获取设备信息  id和版本号
            print('order:接收获取设备信息  id和版本号')
            response_order = OrderPortEnum.RETURN_DEVICE_INFO.value
            response_message = self.current_device.get_device_info()
        elif rs_order == OrderPortEnum.RECV_ENGINEER_START_NO_SNORE.value:
            # 工程师模式下启动止鼾
            pass

        elif rs_order == OrderPortEnum.RECV_ENGINEER_STOP_NO_SNORE.value:
            # 工程师模式下停止止鼾
            pass

        elif rs_order == OrderPortEnum.RECV_ENGINEER_SNORE.value:
            # 工程师模式下获取 是否有鼾声，
            pass

        elif rs_order == OrderPortEnum.RECV_ENGINEER_MOTOR_PRESS.value:
            # 接收 工程师模式下获取 杆头压力传感器数据 命令
            pass

        elif rs_order == OrderPortEnum.RECV_ENGINEER_SHOULDER_PRESS.value:
            # 接收 工程师模式下获取 肩部压力传感器数据 命令
            pass

        elif rs_order == OrderPortEnum.RECV_ENGINEER_LIMIT.value:
            # 接收 工程师模式下获取 是否触发限位功能 命令
            pass

        if response_order:
            # print('send_order:%s' % response_order)
            # print('send_data:%s' % response_order)
            self.send(send_order=response_order, send_data=response_message)


if __name__ == '__main__':
    cc = ComConnected('com7')
