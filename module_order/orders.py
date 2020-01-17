# 接口orders枚举类
# 初始化
from enum import Enum


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

    # --------------- 是否有固件升级文件 ------------------
    # 接收 工程师模式下获取 是否触发限位 命令
    RECV_HAVE_FIRMWRAE_FILE = '2A'
    # 发送 工程师模式下获取 是否触发限位
    RETURN_HAVE_FIRMWRAE_FILE = '2B'

    # --------------- 工程师模式下获取 睡姿算法结果 ------------------
    # 接收 工程师模式下获取 睡姿算法结果
    RECV_ENGINEER_POSITION_RESULT = '2C'
    # 发送 工程师模式下获取 睡姿算法结果
    RETURN_ENGINEER_POSITION_RESULT = '2D'

    # --------------- 工程师模式下切换电机 ------------------
    # 接收 工程师模式下切换电机
    RECV_ENGINEER_CHANGE_MOTOR = '2E'
    # 发送 工程师模式下切换电机
    RETURN_ENGINEER_CHANGE_MOTOR = '2F'
