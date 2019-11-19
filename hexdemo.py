import binascii


def get_check_result(hex_string: str) -> int:
    check_result = 0
    for s in send_str:
        current_result = 0
        i = int(s, 16)
        #  位运算
        for j in range(4):
            v = i >> j & 1
            current_result += v
        check_result += current_result

    return check_result % 2


if __name__ == '__main__':
    # s = '\x30'.encode()
    # s = s.encode('utf8')
    # print(s)
    # s.hex()
    send_str = 'B0000113136165'
    result = get_check_result(send_str)

    print('检查结果为：%s'%result)
