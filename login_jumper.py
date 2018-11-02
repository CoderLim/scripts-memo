#!/usr/bin/python
#coding=utf-8
# code by ls

import os
import pexpect
import pyotp
import time
import struct, fcntl, termios, signal, sys

#
#  重新设置窗口大小
#  如果不设置，登陆ssh后，vim的窗口会很小
#
def normalize_winsize (child):
    #  处理SIGWINCH信号
    def sigwinch_callback (sig, data):
        s = struct.pack("HHHH", 0, 0, 0, 0)
        a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ , s))
        if not child.closed:
            child.setwinsize(a[0], a[1])

    # 当收到窗口尺寸变化信号时调用
    signal.signal(signal.SIGWINCH, sigwinch_callback)
    # 手动触发SIGWINCH信号
    # 因为默认不会有信号发出
    os.kill(os.getpid(), signal.SIGWINCH)

def main():
    userpass = os.environ['LUS']
    username = os.environ['LUN']

    # 堡垒机
    fort_host = 'jump3.oss.letv.cn'
    fort_port = '50022'
    # 跳板机
    jump_host = '10.112.41.59'
    jump_port = '60022'

    # 登陆堡垒机
    fort_cmd = "ssh {username}@{host} -p {port}".format(username=username, host=fort_host, port=fort_port)
    fortress = pexpect.spawn(fort_cmd)

    # 重新设置窗口大小
    normalize_winsize(fortress)
    time.sleep(2)

    try:
        fortress.expect(['password', username, fort_host])
    except Exception as e:
        # The before property will contain all text up to the expected string pattern
        # The after string will contain the text that was matched by the expected pattern
        print(fortress.before)
        print("++1++")
        print(e)

    # 堡垒机密码
    fortress.sendline(userpass)

    try:
        fortress.expect('":h<Enter>" for basics learning.')
    except Exception as e:
        print(fortress.before)
        print("++2++")
        print(e)

    # 登陆跳板机
    jump_cmd = ":ssh {username}@{host}:{port}".format(username=username, host=jump_host, port=jump_port)
    fortress.sendline(jump_cmd)

    try:
        fortress.expect([username, jump_host, "{username}@{host}:{port}'s password:".format(username=username, host=jump_host, port=jump_port)])
    except Exception as e:
        print(fortress.before)
        print("++3++")
        print(e)

    # 跳板机密码
    ttop = pyotp.TOTP('4JUGKPB4V5Z4NHUQNGAGAEBRFA')
    fortress.sendline(userpass + ttop.now())
    # 保持登陆
    fortress.sendline('export TIMEOUT=0')
    fortress.interact()


if __name__=='__main__':
    main()
