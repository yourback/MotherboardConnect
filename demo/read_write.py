import os
import random

if __name__ == '__main__':
    # 读取
    # f_r = open("1.17a.zip", 'rb')
    # b = f.read(2)
    # f.close()
    # print(b)
    # 写入
    f_w = open('c.zip', 'wb')

    # 读取文件大小
    f_r_size = os.path.getsize('1.17a.zip')
    print("%s字节" % f_r_size)

    package_nums = f_r_size // 43 + 1
    print("分成%s包" % package_nums)
    last_package_size = f_r_size % 43
    print("最后一包大小%s字节" % last_package_size)
    # 打开文件
    with open("1.17a.zip", 'rb') as f_r:
        i = 1
        while i < package_nums + 1:
            if i == package_nums:
                s = f_r.read(last_package_size)
                print('最后一包数据：%s' % s.hex())
                # f_w.write(bytes(s.hex(), encoding='utf8'))
                f_w.write(bytes.fromhex(s.hex()))
            else:
                f_r.seek((i - 1) * 43)
                s = f_r.read(43)
                # print('二进制数据：%s' % s)
                # print('二进制数据：%s' % bytes.fromhex(s.hex()))

                # 随机false 或者 true

                print('第%s包数据：%s' % (i, s.hex()))

                print("传输成功")
                f_w.seek((i - 1) * 43)
                f_w.write(bytes.fromhex(s.hex()))

            if random.randint(0, 1):
                print('传输失败')
                # 传输失败
                continue

            i += 1

    f_w.close()
