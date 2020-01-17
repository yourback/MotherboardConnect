import os
import queue
import random
import threading

from module_device.device import Device
from module_order.orders import OrderPortEnum


class OrderManager(object):
    def __init__(self, queue_to_device: queue, queue_from_device: queue, queue_to_message: queue,
                 queue_from_message: queue, pool: list):
        self.queue_to_device = queue_to_device
        self.queue_from_device = queue_from_device
        self.queue_to_message = queue_to_message
        self.queue_from_message = queue_from_message
        self.pool = pool

        # 新建设备
        self.current_device = Device(queue_from_device)

    def ready(self):
        t_recv_from_device = threading.Thread(target=self.recv_from_device, args=())
        self.pool.append(t_recv_from_device)
        t_recv_from_message = threading.Thread(target=self.recv_from_message, args=())
        self.pool.append(t_recv_from_message)

    def recv_from_device(self):
        """
        从设备模块收到的消息
        :return:
        """
        while True:
            data = self.queue_from_device.get(block=True, timeout=None)
            response_order = OrderPortEnum.RETURN_GET_DEVICE_WORK_MODE.value
            # 获取设备工作状态
            response_message = data
            self.queue_to_message.put((response_order, response_message))

    def recv_from_message(self):
        """
        从消息模块收到的消息
        :return:
        """
        while True:
            data = self.queue_from_message.get(block=True, timeout=None)
            self.order_analysis(data)

    # 文件路径

    firmware_file = "../firmware/firmware_update.zip"

    f_w = None
    # 升级文件总包数
    package_num = 0

    # 当前发送文件的路径
    f_r_path = ''
    # 当前发送的文件
    f_r = None
    # 包数
    pn = 0
    # 最后一包的大小
    last_pn_size = 0

    # 命令解析
    def order_analysis(self, data):
        """
        order analysis order
        :return:
        """
        rs_order = data[:2]
        rs_message = data[2:]

        response_order = ''
        response_message = ''

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
            print("设置某个电机开始工作")
            # 电机号
            motor_num = rs_message[0:2]
            # 方向 0 上 1下
            move_directions = rs_message[2:4] == 1
            # 速度挡位 1-5
            move_speed = rs_message[4:6]
            # 时间
            move_duration = rs_message[6:8]
            print("第%s个电机向%s以%s挡位运动%s秒" % (motor_num, "上" if move_directions else "下", move_speed, move_duration))
            response_order = OrderPortEnum.RETURN_SET_DEVICE_MOTOR_RUN.value
            response_message = "0%d" % random.randint(0, 1)
        elif rs_order == OrderPortEnum.RECV_SET_DEVICE_MOTOR_STOP_RUN.value:
            # 设置某个电机停止工作
            print("设置某个电机停止工作")
            response_order = OrderPortEnum.RETURN_SET_DEVICE_MOTOR_STOP_RUN.value
            response_message = "0%d" % random.randint(0, 1)
        elif rs_order == OrderPortEnum.RECV_SET_DEVICE_TIME.value:
            # 设置开发板时间功能
            pass

        elif rs_order == OrderPortEnum.RECV_START_SEND_FILE.value:
            # 开启文件传输
            print('开启文件传输')
            file_type = rs_message[:2]
            print('需要的文件类型：%s' % file_type)
            file_date = rs_message[2:]
            print('需要的文件日期：%s' % file_date)
            # 查询文件是否存在

            if file_type == '01':
                file_name = 'motor_file.db'
            elif file_type == '02':
                file_name = 'snore_file.db'
            elif file_type == '03':
                file_name = 'position_file.db'
            elif file_type == '04':
                file_name = 'snore_intervention.db'
            elif file_type == '05':
                file_name = 'record_sound_file.wav'
            elif file_type == '06':
                file_name = 'sleep_data.txt'
            else:
                file_name = 'no_file'

            if file_type == "05":
                self.f_r_path = "dbdata/%s" % file_name
            else:
                self.f_r_path = "dbdata/%s/%s" % (file_date, file_name)
            print('文件路径%s' % self.f_r_path)
            if os.path.exists(self.f_r_path):
                print('%s存在' % file_name)
                # 查看一共多少包，每包43字节
                file_size = os.path.getsize(self.f_r_path)
                print('文件大小：%s字节' % file_size)
                self.pn = file_size // 43 + 1
                self.last_pn_size = file_size % 43
                # 总包数转为十六进制字符串
                pn_hex_str = hex(self.pn).replace("0x", "")
                # 变成两字节
                while len(pn_hex_str) < 4:
                    pn_hex_str = "0" + pn_hex_str

                response_message = pn_hex_str
                print('response_message:%s' % response_message)
                print('文件 %s 包数:%s' % (file_name, self.pn))
                # 打开文件
                self.f_r = open(self.f_r_path, 'rb')
            else:
                # 不存在
                response_message = "0000"
            response_order = OrderPortEnum.RETURN_PACKAGE_NUM.value
        elif rs_order == OrderPortEnum.RECV_PHONE_REQUEST_SOMEONE_PACKAGE.value:
            # 手机已经准备好接收文件
            i = int(rs_message, 16)
            # 如果发来的是0  说明手机接收完成 关闭文件 返回 ’0000
            if i == 0:
                print('文件申请完成')
                if self.f_r is not None:
                    self.f_r.close()
                    self.f_r = None
                response_message = '0000'
            else:
                print('手机申请第%s包文件数据：' % i)
                # 如果发来的不是0 则申请具体包数
                # 读取对应包数的数据
                if self.f_r is not None:
                    # 移动指针到读取位置
                    self.f_r.seek((i - 1) * 43)
                    # 如果 手机申请的包不是最后一包 位置为 (i-1) * 43 读取43字节
                    if i != self.pn:
                        print('手机申请的不是最后一包：%s' % i)
                        read_byte = self.f_r.read(43)
                        print('读取的二进制：%s' % read_byte)
                        print('转化为十六进制字符串：%s' % read_byte.hex())
                        response_message = rs_message + read_byte.hex()
                    # 如果 手机申请的是最后一包 位置为 (i-1) * 43 读取43字节
                    else:
                        print('手机申请的是最后一包：%s' % i)
                        read_byte = self.f_r.read(self.last_pn_size)
                        print('读取的二进制：%s' % read_byte)
                        print('转化为十六进制字符串：%s' % read_byte.hex())
                        response_message = rs_message + read_byte.hex()

            response_order = OrderPortEnum.RETURN_SEND_PACKAGE.value
        elif rs_order == OrderPortEnum.RECV_UPDATE.value:
            # 开启升级功能
            self.package_num = int(rs_message, 16)
            print("开启固件升级功能,总包数:%s" % self.package_num)
            response_order = OrderPortEnum.RETURN_READY_RECV_UPDATE_FILE.value
            response_message = rs_message
        elif rs_order == OrderPortEnum.RECV_PACKAGE.value:
            # 手机端传送升级文件（分包）
            # 新建升级文件
            if self.f_w is None:
                print('文件为空，打开文件')
                self.f_w = open(self.firmware_file, 'wb')

            recv_package_hex = rs_message[:4]
            recv_package_int = int(recv_package_hex, 16)

            recv_package_content = rs_message[4:]
            print('手机传送升级文件中...当前包:%s' % recv_package_int)
            print('文件内容：%s' % recv_package_content)
            # 如果收到的包数等于0 且 内容等于 '00'的话 关闭文件  并删除文件
            if recv_package_int == 0 and recv_package_content == '00':
                print('传输终止，关闭并删除文件')
                self.f_w.close()
                os.remove('../firmware/firmware_update.zip')
                self.f_w = None
                return

            # 写文件位置
            write_position = 43 * (recv_package_int - 1)
            # 移动写文件指针
            self.f_w.seek(write_position)
            # 写文件
            self.f_w.write(bytes.fromhex(recv_package_content))
            # 如果文件是最后一包关闭文件
            if self.package_num == recv_package_int:
                print('传输完毕，关闭文件')
                self.package_num = 0
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
            print("工程师模式下启动止鼾")
            # 第1字节 00 无鼾声 01 有鼾声
            # 第2字节 00 侧卧  01 仰卧
            has_Snore = (int(rs_message[1:2], 16) == 1)
            side_sleep = (int(rs_message[3:4], 16) == 0)
            print("启动止鼾：%s %s" % ("有鼾声" if has_Snore else "无鼾声", "侧卧" if side_sleep else "仰卧"))
            response_order = OrderPortEnum.RETURN_ENGINEER_START_NO_SNORE.value
            response_message = "0%d" % random.randint(0, 1)

        elif rs_order == OrderPortEnum.RECV_ENGINEER_STOP_NO_SNORE.value:
            # 工程师模式下停止止鼾
            print("工程师模式下停止止鼾")
            response_order = OrderPortEnum.RETURN_ENGINEER_STOP_NO_SNORE.value
            response_message = "0%d" % random.randint(0, 1)

        elif rs_order == OrderPortEnum.RECV_ENGINEER_SNORE.value:
            # 工程师模式下获取 是否有鼾声，
            print("工程师模式下获取 是否有鼾声")
            response_order = OrderPortEnum.RETURN_ENGINEER_SNORE.value
            response_message = "0%d" % random.randint(0, 1)
        elif rs_order == OrderPortEnum.RECV_ENGINEER_MOTOR_PRESS.value:
            # 接收 工程师模式下获取 杆头压力传感器数据 命令
            print("工程师模式下获取 杆头压力传感器数据")
            response_order = OrderPortEnum.RETURN_ENGINEER_MOTOR_PRESS.value
            which_press = "0%d" % random.randint(1, 6)
            singles = "0%d" % random.randint(1, 9)
            deciles = "0%d" % random.randint(1, 9)
            percentile = "0%d" % random.randint(1, 9)
            Thousands = "0%d" % random.randint(1, 9)
            response_message = which_press + singles + deciles + percentile + Thousands
        elif rs_order == OrderPortEnum.RECV_ENGINEER_SHOULDER_PRESS.value:
            # 接收 工程师模式下获取 肩部压力传感器数据 命令
            # 第几行
            i = int(rs_message, 16)
            print("工程师模式下获取 第%s行肩部压力传感器数据" % i)
            response_order = OrderPortEnum.RETURN_ENGINEER_SHOULDER_PRESS.value
            which_row = "0%d" % random.randint(0, 3)
            # 随机生成6位16进制数据
            response_message = rs_message + ''.join([random.choice("0123456789ABCDEF") for _ in range(6)])
        elif rs_order == OrderPortEnum.RECV_ENGINEER_LIMIT.value:
            # 接收 工程师模式下获取 是否触发限位功能 命令
            print("工程师模式下获取 是否触发限位功能")
            response_order = OrderPortEnum.RETURN_ENGINEER_LIMIT.value
            response_message = "0%d" % random.randint(0, 2)

        elif rs_order == OrderPortEnum.RECV_HAVE_FIRMWRAE_FILE.value:
            # 接收 是否有升级固件文件 命令
            response_order = OrderPortEnum.RETURN_HAVE_FIRMWRAE_FILE.value
            response_message = "00"
            if os.path.exists(self.firmware_file):
                response_message = "01"
        elif rs_order == OrderPortEnum.RECV_ENGINEER_POSITION_RESULT.value:
            # 工程师模式下获取 睡姿算法结果
            response_order = OrderPortEnum.RETURN_ENGINEER_POSITION_RESULT.value
            result_int = random.randint(0, 2)
            response_message = "0%d" % result_int
        elif rs_order == OrderPortEnum.RECV_ENGINEER_CHANGE_MOTOR.value:
            print('切换到 %s 号电机' % int(rs_message, 16))
            # 工程师模式下切换电机
            response_order = OrderPortEnum.RETURN_ENGINEER_CHANGE_MOTOR.value
            response_message = "00"

        if response_order:
            print('send_order:%s' % response_order)
            print('send_data:%s' % response_message)
            # self.send(send_order=response_order, send_data=response_message)
            self.queue_to_message.put((response_order, response_message))
