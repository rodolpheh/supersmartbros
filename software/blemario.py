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

stop_curses = False
stop_drawing_logs = False

threads = []


def draw_logs(stdscr, win, winyx, winpos):
    global stop_drawing_logs
    while not stop_drawing_logs:
        stdscr.clear()
        stdscr.border()

        height, width = stdscr.getmaxyx()

        with lock:
            logs = shared["logs"]
            start = 0 if (len(logs) < height - 2) else (len(logs) - height + 2)
            for index, log in enumerate(logs[start:]):
                stdscr.addstr(index + 1, 1, str(log))

        stdscr.move(winyx()[0], winyx()[1])
        stdscr.refresh()

        time.sleep(0.3)

    with lock:
        shared["logs"].append("Stopping log drawing thread")


def draw_screen(stdscr):
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    height, width = stdscr.getmaxyx()
    win = curses.newwin(1, width - 1, height - 1,  0)
    winLogs = curses.newwin(height - 1, width, 0, 0)

    logsThread = Thread(target=draw_logs, args=(
        winLogs, win,
        lambda: win.getyx(),
        lambda: win.getparyx()
    ))
    logsThread.start()
    threads.append(logsThread)

    global stop_curses
    global device
    try:
        while True:
            win.clear()

            height, width = stdscr.getmaxyx()

            tb = curses.textpad.Textbox(win)
            tb.stripspaces = True
            text = tb.edit()

            if device is not None:
                device.write(text)

            win.refresh()

    except KeyboardInterrupt:
        pass

    with lock:
        shared["logs"].append("Stopping curses")
    global stop_drawing_logs
    stop_drawing_logs = True


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
