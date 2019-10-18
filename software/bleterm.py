import gatt
from threading import Thread
import time
from dbus.exceptions import DBusException

from argparse import ArgumentParser

writeCharacteristic = None
logs = []
setup = False

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        global logs
        logs.append("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        global logs
        logs.append("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        global setup
        setup = True

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        global logs
        logs.append("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        global logs
        logs.append("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            logs.append("[%s]\tService [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                logs.append("[%s]\t\tCharacteristic [%s]" % (self.mac_address, characteristic.uuid))
                if characteristic.uuid == "6e400003-b5a3-f393-e0a9-e50e24dcca9e":
                    characteristic.read_value()
                    characteristic.enable_notifications()
                if characteristic.uuid == "6e400002-b5a3-f393-e0a9-e50e24dcca9e":
                    global writeCharacteristic
                    writeCharacteristic = characteristic
                    if args.write is not None:
                        writeCharacteristic.write_value(args.write.encode())
                for descriptor in characteristic.descriptors:
                    logs.append("[%s]\t\t\tDescriptor [%s] (%s)" % (self.mac_address, descriptor.uuid, descriptor.read_value()))
        global setup
        setup = True

    def descriptor_read_value_failed(self, descriptor, error):
        global logs
        logs.append('descriptor_value_failed')

    def characteristic_value_updated(self, characteristic, value):
        global logs
        logs.append("<-| {}".format(value))

    def characteristic_write_value_failed(self, characteristic, error):
        global logs
        logs.append("Error writing value: {}".format(error))


def draw_logs(stdscr, win, stop, winyx, winpos):
    global logs
    while True:
        stdscr.clear()

        height, width = stdscr.getmaxyx()
        curses.textpad.rectangle(stdscr, 0, 0, height - 2, width - 1)
        start = 0 if (len(logs) < height - 3) else (len(logs) - height + 3)

        for index, log in enumerate(logs[start:]):
            stdscr.addstr(index + 1, 1, log)

        stdscr.move(winyx()[0], winyx()[1])

        stdscr.refresh()
        win.refresh()

        if stop():
            break

        time.sleep(0.3)

def draw_menu(stdscr):
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    height, width = stdscr.getmaxyx()
    win = curses.newwin(1, width - 1, height - 1,  1)
    winLogs = curses.newwin(height - 1, width, 0, 0)
    promptWin = curses.newwin(2, 2, height - 1, 0)

    stop_thread = False
    logsThread = Thread(target = draw_logs, args=(winLogs, win, lambda : stop_thread, lambda : win.getyx(), lambda : win.getparyx()))
    logsThread.start()

    try:
        while True:
            win.clear()
            promptWin.clear()

            height, width = stdscr.getmaxyx()

            promptWin.addstr(0, 0, ">")

            tb = curses.textpad.Textbox(win)
            tb.stripspaces = True
            text = tb.edit()

            # win.refresh()
            promptWin.refresh()

            writeCharacteristic.write_value(text.encode())
    except KeyboardInterrupt:
        stop_thread = True
        logsThread.join()
        return


if __name__ == "__main__":
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    arg_parser.add_argument('--monitor', '-m', help="Open the monitor (very buggy !)", action='store_true', required=False)
    arg_parser.add_argument('--write', '-w', help="Write a string", required=False)
    args = arg_parser.parse_args()

    print("Connecting...")

    manager = gatt.DeviceManager(adapter_name='hci0')

    device = AnyDevice(manager=manager, mac_address=args.mac_address)
    device.connect()

    thread = Thread(target = manager.run)
    thread.start()

    if args.monitor:
        import curses
        import curses.textpad
        curses.wrapper(draw_menu)

    try:
        while not setup:
            pass
    except KeyboardInterrupt:
        pass
    
    print('Quitting...')
    try:
        device.disconnect()
    except DBusException as error:
        print(error)
    manager.stop()
    thread.join()
    curses.nocbreak()
    curses.echo()
