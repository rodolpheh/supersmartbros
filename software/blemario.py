import gatt
from threading import Thread, Lock
from dbus.exceptions import DBusException
from blecomm import BLEComm
from bleterm import BLETerm

from argparse import ArgumentParser

lock = Lock()
logs = []


def send_and_wait(device, message):
    device.write(args.write)
    while not device.message_sent:
        pass


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
        help=("Select the mode (monitor, write, listen)."
              "The default is monitor"),
        action='store',
        required=False,
        default='monitor'
    )
    arg_parser.add_argument(
        '--write', '-w',
        help="The string to write in 'write' mode",
        required=False
    )
    arg_parser.add_argument(
        '--debug', '-d',
        help=("Print logs (does nothing with --monitor). "
              "This is off by default"),
        action='store_false',
        required=False
    )
    args = arg_parser.parse_args()

    if args.mode == 'monitor':
        bleterm = BLETerm(args.mac_address)
        bleterm.open()
        bleterm.close()
        exit(0)
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
    else:
        print("Unrecognized mode: {}".format(args.mode))
