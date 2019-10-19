import gatt
from threading import Thread, Lock
import time
from dbus.exceptions import DBusException
from blecomm import BLEComm

from argparse import ArgumentParser

lock = Lock()
shared = {
    "logs": []
}

threads = []


def draw_screen(stdscr):
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()
    stdscr.nodelay(True)

    curses.echo()

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

    global stop_curses
    global device
    try:
        while True:
            win.clear()
            winLogs.clear()
            win.border()
            winLogs.border()

            with lock:
                logs = shared["logs"]
                start = 0 if (len(logs) < height - 5) else (len(logs) - height + 5)
                for index, log in enumerate(logs[start:]):
                    winLogs.addstr(index + 1, 1, str(log))

            win.addstr(1, 1, current_str)

            new_char = win.getch(1, char_pos)

            if new_char != -1 and new_char <= 255:
                if new_char == 10 and device is not None:
                    device.write(current_str)
                    current_str = ""
                    char_pos = 1
                elif new_char == 8 or new_char == 127 or new_char == curses.KEY_BACKSPACE:
                    char_pos -= 1
                    current_str = current_str[:-1]
                else:
                    char_pos += 1
                    current_str += chr(new_char)

            winLogs.refresh()
            win.refresh()
    except KeyboardInterrupt:
        pass

    with lock:
        shared["logs"].append("Stopping curses")


def send_and_wait(device, message):
    device.write(args.write)
    while not device.message_sent:
        pass


if __name__ == "__main__":
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument(
        'mac_address',
        help="MAC address of device to connect"
    )
    arg_parser.add_argument(
        '--monitor', '-m',
        help="Open the monitor (very buggy !)",
        action='store_true',
        required=False
    )
    arg_parser.add_argument(
        '--write', '-w',
        help="Write a string",
        required=False
    )
    args = arg_parser.parse_args()

    print("Connecting...")

    manager = gatt.DeviceManager(adapter_name='hci0')

    device = BLEComm(
        shared,
        lock,
        not args.monitor,
        manager=manager,
        mac_address=args.mac_address
    )
    device.connect()

    blecomm_thread = Thread(target=manager.run)
    blecomm_thread.start()
    threads.append(blecomm_thread)

    try:
        while not device.is_setup():
            pass
        if args.write is not None:
            send_and_wait(device, args.write)
    except KeyboardInterrupt:
        pass

    if args.monitor:
        import curses
        import curses.textpad
        curses.wrapper(draw_screen)

    print('Quitting...')
    try:
        device.disconnect()
        print("Device disconnected")
    except DBusException as error:
        print(error)

    manager.stop()
    for thread in threads:
        thread.join()
