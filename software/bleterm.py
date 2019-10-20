from dbus.exceptions import DBusException
from threading import Thread, Lock
from blecomm import BLEComm
import curses
import gatt
from os import read, ttyname, write
import pty


class BLETerm():

    def __init__(self, mac_address, *args, **kwargs):
        self.manager = gatt.DeviceManager(adapter_name='hci0')
        self.logs = []
        self.lock = Lock()

        self.serial_master = None
        self.serial_slave = None
        self.first_read = True

        self.device = BLEComm(
            self.logs,
            self.lock,
            False,
            on_message_received=self.on_message_received,
            manager=self.manager,
            mac_address=mac_address
        )
        self.device.connect()

        self.blecomm_thread = Thread(target=self.manager.run)
        self.blecomm_thread.start()

    def open_serial_bridge(self):
        self.serial_master, self.serial_slave = pty.openpty()
        s_name = ttyname(self.serial_slave)
        m_name = ttyname(self.serial_master)

        print("Slave: {}".format(s_name))
        print("Master: {}".format(m_name))

        try:
            while not self.device.is_setup():
                pass
            print("Connected !")
            res = b""
            while True:
                c = read(self.serial_master, 1)
                res += c
                if (res.endswith(b'\r')
                        or res.endswith(b'\n')
                        or res.endswith(b"\r\n")):
                    formatted = res.decode("utf-8").strip()
                    if len(formatted) > 0 and not self.first_read:
                        formatted += '\n'
                        formatted = formatted.encode()
                        print("BLE <- : {}".format(
                            formatted))
                        self.device.write_raw(formatted)

                    self.first_read = False
                    res = b''
        except KeyboardInterrupt:
            pass

    def open_monitor(self):
        curses.wrapper(self.draw_screen)

    def close(self):
        try:
            self.device.disconnect()
            print("Device disconnected")
        except DBusException as error:
            print(error)

        self.manager.stop()
        self.blecomm_thread.join()

    def on_message_received(self, message):
        if self.serial_master is not None and not self.first_read:
            write(self.serial_master, message)
            print("BLE -> : {}".format(message))
        self.first_read = True

    def draw_screen(self, stdscr):
        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()
        stdscr.nodelay(True)

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        height, width = stdscr.getmaxyx()
        win = curses.newwin(3, width, height - 3,  0)
        winLogs = curses.newwin(height - 3, width, 0, 0)

        win.timeout(300)
        win.clear()
        winLogs.clear()
        win.border()
        winLogs.border()
        win.refresh()
        winLogs.refresh()

        char_pos = 1
        current_str = ""

        try:
            while True:
                win.clear()
                winLogs.clear()
                win.border()
                winLogs.border()

                with self.lock:
                    start = (0 if (len(self.logs) < height - 5)
                             else (len(self.logs) - height + 5))
                    for index, log in enumerate(self.logs[start:]):
                        winLogs.addstr(index + 1, 1, str(log))

                win.addstr(1, 1, current_str)

                new_char = win.getch(1, char_pos)

                if new_char != -1 and new_char <= 255:
                    if new_char == 10:
                        self.device.write(current_str)
                        current_str = ""
                        char_pos = 1
                    elif (new_char == 8
                            or new_char == 127
                            or new_char == curses.KEY_BACKSPACE):
                        char_pos -= 1
                        current_str = current_str[:-1]
                    else:
                        char_pos += 1
                        current_str += chr(new_char)

                winLogs.refresh()
                win.refresh()
        except KeyboardInterrupt:
            pass

        with self.lock:
            self.logs.append("Stopping curses")
