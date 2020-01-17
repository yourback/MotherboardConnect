import queue

from module_comm.comm_manager import PortManager
from module_message.message_manager import MessageManager
from module_order.order_manager import OrderManager


class AppManager(object):
    def __init__(self):
        # 线程池
        self.threading_pool = []
        # 模块之间的通讯总线初始化
        # 通信模块与消息处理模块之间的管道
        comm2message = queue.Queue(maxsize=-1)
        message2comm = queue.Queue(maxsize=-1)
        # 消息处理模块与命令模块之间的
        message2order = queue.Queue(maxsize=-1)
        order2message = queue.Queue(maxsize=-1)
        # 命令模块与设备模块之间的
        order2device = queue.Queue(maxsize=-1)
        device2order = queue.Queue(maxsize=-1)

        # 模块初始化
        # 通讯模块初始化
        self.pm = PortManager('com7', comm2message, message2comm, self.threading_pool)
        self.pm.open().ready()
        print('通讯模块初始化完成')
        # 消息处理模块初始化
        self.msg = MessageManager(message2order, order2message, message2comm, comm2message,
                                  self.threading_pool)
        self.msg.ready()
        print('消息处理模块初始化完成')
        # 命令模块初始化
        self.order = OrderManager(order2device, device2order, order2message, message2order,
                                  self.threading_pool)
        self.order.ready()
        print('命令模块初始化完成')
        # 设备模块初始化

    def start(self):
        for t in self.threading_pool:
            t.start()
        for t in self.threading_pool:
            t.join()


if __name__ == '__main__':
    pm = AppManager()
    pm.start()
    print('主线程结束')
