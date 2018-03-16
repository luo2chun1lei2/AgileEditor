#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 模仿程序script来实现, 参考pymux。
# 创建pty，然后再fork一个进程（shell），通过pty控制shell。
# stty -a 可以查看当前终端的attr

# 测试注意
# 启动bash后，Ctrl+H等快捷键、vi、man、top、ctrl+z等功能。
# 改变窗口大小后，用stty -a查看终端大小是否发生改变。
# exit/ctrl+D退出shell后，再输入命令和查看man/vi是否正常。

import os, sys, locale, time, struct
import select, fcntl, posix, signal
import pyte, pty, termios
import errno

# 保存的之前的终端设定。
original_pty_attr = None

def on_exit():
    # 关闭进程时，必须恢复之前的终端设定，否则将让父进程的控制台输入无回显。
    global original_pty_attr
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, original_pty_attr)

class MyShell:

    def __init__(self):
        self.child_pid = -1
        self.master_fd = -1
        self.win_size = None

    def print_str(self, str):
        sys.stdout.write(str)
        sys.stdout.flush()

    def on_signal(self, signum, frame):

        if self.child_pid == -1:
            return

        if signum == signal.SIGCHLD:
            # wait for child process terminating.
            os.waitpid(self.child_pid, 0)
            sys.exit()
        elif signum == signal.SIGTERM or signum == signal.SIGINT or signum == signal.SIGQUIT:
            # send SIGTERM to child.
            os.kill(self.child_pid, signal.SIGTERM)
        elif signum == signal.SIGWINCH:
            # set WINSIZE of child.
            size = struct.pack('HHHH', 0, 0, 0, 0)
            size = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, size)  # get size
            # 修改master_fd的窗口大小，就是修改slave_fd的窗口大小。
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, size)  # set size
        else:
            sys.exit(1)

    def start(self):
        global original_pty_attr

        # 保存当前终端的attr，为了后面恢复。
        original_pty_attr = termios.tcgetattr(sys.stdin.fileno())

        # 设定进程关闭后的动作。
        sys.exitfunc = on_exit

        win_size = struct.pack('HHHH', 0, 0, 0, 0)
        win_size = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, win_size)  # get win_size

        self.child_pid, self.master_fd = os.forkpty()

        if self.child_pid == 0:  # in child process
            fcntl.ioctl(sys.stdin.fileno(), termios.TIOCSWINSZ, win_size)  # set win_size

            os.execv('/bin/bash', [' -i'])

        else:  # in parent proces
            signal.signal(signal.SIGCHLD, self.on_signal)
            signal.signal(signal.SIGWINCH, self.on_signal)
            signal.signal(signal.SIGTERM, self.on_signal)
            signal.signal(signal.SIGINT, self.on_signal)
            signal.signal(signal.SIGQUIT, self.on_signal)

            # 非常规输入。
            tc_attr = termios.tcgetattr(sys.stdin.fileno())
            tc_attr[3] = tc_attr[3] & ~termios.ICANON & ~termios.ECHO & ~termios.ISIG
            tc_attr[6][termios.VMIN] = 1
            tc_attr[6][termios.VTIME] = 0
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, tc_attr)

            while True:
                try:
                    # 这里就应该是sys.stdin，而不是sys.stdin.fileno(), 而master_fd则必须是fd。 奇怪！
                    rs, ws, es = select.select([sys.stdin, self.master_fd], [], [], 1)
                    for s in rs:
                        if s == sys.stdin:  # 来自控制台的输入，是用户的命令
                            ch = os.read(sys.stdin.fileno(), 16)
                            os.write(self.master_fd, ch)

                        else:  # 来自SHELL的输出，是用户命令执行的结果。
                            # 得到运行结果
                            try:
                                str_rlt = os.read(self.master_fd, 2048)  # <--- TODO 有大小，是否不应该要！
                                # 显示结果
                                self.print_str(str_rlt)
                            except:
                                # 如果子进程销毁，这里简单的用一个异常捕获，应该用信号捕获。
                                sys.exit()
                # 虽然signal设定了信号处理函数，但是select还是会被打断！ 但是还需要等待 CHILD 关闭。
                except select.error, (_errno, _strerror):
                    # select一般的异常都是被打断，就是EINTR错误，可以用“if _errno == errno.EINTR:”来判断。
                    pass

                except:
                    # 这是真正的子进程被关闭。
                    break

def main(argv):
    locale.setlocale(locale.LC_ALL, locale='en_US.UTF-8')

    shell = MyShell()
    shell.start()

if __name__ == '__main__':
    main(sys.argv)
