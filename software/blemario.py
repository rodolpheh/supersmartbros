import gatt
from threading import Thread, Lock
from dbus.exceptions import DBusException
from blecomm import BLEComm
from bleterm import BLETerm
import sys
import hashlib
import time

from argparse import ArgumentParser

lock = Lock()
logs = []


def send_and_wait(device, message):
    device.write(args.write)
    while not device.message_sent:
        pass


def arg_in_argv(args):
    for arg in args:
        if arg in sys.argv:
            return True
    return False


def is_mode(mode):
    if "--mode" not in sys.argv and "-m" not in sys.argv and mode != "monitor":
        return False
    index = (sys.argv.index("-m")
             if "-m" in sys.argv
             else sys.argv.index("--mode"))
    return sys.argv[index + 1] == mode


def file_hash(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        description="Communicate with the BLE of Super Smart Bros"
    )
    arg_parser.add_argument(
        'mac_address',
        help="MAC address of device to connect"
    )
    arg_parser.add_argument(
        '--mode',
        help=("Select the mode. "
              "The default is monitor"),
        action='store',
        required=False,
        default='monitor',
        choices=["monitor", "write", "listen", "serial", "watch"]
    )
    arg_parser.add_argument(
        '--write', '-w',
        help="The string to write in 'write' mode",
        required=is_mode("write")
    )
    arg_parser.add_argument(
        '--debug', '-d',
        help=("Print logs (does nothing with --monitor). "
              "This is off by default"),
        action='store_true',
        required=False
    )
    arg_parser.add_argument(
        '--file', '-f',
        help=("The file to watch"),
        action='store',
        required=is_mode("watch")
    )
    args = arg_parser.parse_args()

    if args.mode == 'listen' and args.debug:
        print("INFO: the --debug/-d argument is turned "
              "on by default with the listen mode. It is then"
              "unnecessary.")

    if args.mode != 'write' and args.write is not None:
        print(
            "INFO: the --write/-w argument works only with the write mode")

    if args.mode != 'watch' and args.file is not None:
        print("INFO: the --file/-f argument works only with the watch mode")

    if args.mode == 'monitor' or args.mode == 'serial':
        bleterm = BLETerm(args.mac_address)
        if args.mode == 'monitor':
            bleterm.open_monitor()
            bleterm.close()
        elif args.mode == 'serial':
            bleterm.open_serial_bridge()
            bleterm.close()
    elif args.mode == 'write' or args.mode == 'listen':
        print("Connecting...")

        manager = gatt.DeviceManager(adapter_name='hci0')

        debug = args.debug
        if args.mode == 'listen':
            debug = True

        device = BLEComm(
            logs,
            lock,
            debug,
            manager=manager,
            mac_address=args.mac_address
        )
        device.connect()

        blecomm_thread = Thread(target=manager.run)
        blecomm_thread.start()

        try:
            if args.mode == 'write':
                while not device.is_setup():
                    pass
                if args.write is not None:
                    print("Sending message: {}".format(args.write))
                    send_and_wait(device, args.write)
            elif args.mode == 'listen':
                while True:
                    pass
        except KeyboardInterrupt:
            pass

        print('Quitting...')
        try:
            device.disconnect()
            print("Device disconnected")
        except DBusException as error:
            print(error)

        manager.stop()
        blecomm_thread.join()
    elif args.mode == "watch":
        print("Connecting...")

        previous_hash = None
        hash = file_hash(args.file)

        manager = gatt.DeviceManager(adapter_name='hci0')

        device = BLEComm(
            logs,
            lock,
            args.debug,
            manager=manager,
            mac_address=args.mac_address
        )
        device.connect()

        blecomm_thread = Thread(target=manager.run)
        blecomm_thread.start()

        try:
            while not device.is_setup():
                pass
            print("Connected !")
            print("Watching file {}".format(args.file))
            while True:
                hash = file_hash(args.file)
                if hash != previous_hash:
                    print("File changed")
                    with open(args.file, 'rb') as f:
                        file_content = f.read().strip()
                        device.write_raw(file_content)
                previous_hash = hash
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

        print('Quitting...')
        try:
            device.disconnect()
            print("Device disconnected")
        except DBusException as error:
            print(error)

        manager.stop()
        blecomm_thread.join()
    else:
        print("Unrecognized mode: {}".format(args.mode))
