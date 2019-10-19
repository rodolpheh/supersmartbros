import gatt


class BLEComm(gatt.Device):
    def __init__(self, shared, lock, debug, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared = shared
        self.lock = lock
        self.debug = debug

        self.message_sent = True
        self.write_characteristic = None
        self.setup = False

    def get_safely(self, key):
        with self.lock:
            data = self.shared[key]
        return data

    def set_safely(self, key, value):
        with self.lock:
            self.shared[key] = value
        return

    def append_safely(self, key, value):
        with self.lock:
            if self.debug:
                print(value)
            self.shared[key].append(value)
        return

    def connect_succeeded(self):
        super().connect_succeeded()
        self.append_safely("logs", "[{}] Connected".format(self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        self.append_safely(
            "logs",
            "[{}] Connection failed: {}".format(self.mac_address, str(error))
        )
        self.set_safely("setup", True)

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        self.append_safely("logs", "[%s] Disconnected" % (self.mac_address))
        self.set_safely("setup", True)

    def services_resolved(self):
        super().services_resolved()

        self.append_safely(
            "logs", "[{}] Resolved services".format(self.mac_address)
        )

        for service in self.services:
            self.append_safely(
                "logs", "[{}]\tService [{}]".format(
                    self.mac_address,
                    service.uuid
                )
            )

            for characteristic in service.characteristics:
                self.append_safely(
                    "logs",
                    "[{}]\t\tCharacteristic [{}]".format(
                        self.mac_address,
                        characteristic.uuid
                    )
                )

                # Register the read characteristic when found
                if (characteristic.uuid ==
                        "6e400003-b5a3-f393-e0a9-e50e24dcca9e"):
                    characteristic.read_value()
                    characteristic.enable_notifications()

                # Register the write characteristic when found
                if (characteristic.uuid ==
                        "6e400002-b5a3-f393-e0a9-e50e24dcca9e"):
                    self.set_safely("writeCharacteristic", characteristic)
                    self.write_characteristic = characteristic

                for descriptor in characteristic.descriptors:
                    try:
                        self.append_safely(
                            "logs",
                            "[{}]\t\t\tDescriptor [{}] ({})".format(
                                self.mac_address,
                                descriptor.uuid,
                                descriptor.read_value()
                            )
                        )
                    except AttributeError as err:
                        self.append_safely(
                            "logs",
                            "[{}]\t\t\tDescriptor [{}] ({})".format(
                                self.mac_address,
                                descriptor.uuid,
                                err
                            )
                        )

        self.set_safely("setup", True)
        self.setup = True

    def descriptor_read_value_failed(self, descriptor, error):
        self.append_safely("logs", 'descriptor_value_failed')

    def characteristic_value_updated(self, characteristic, value):
        self.append_safely("logs", "<-| {}".format(value))

    def characteristic_write_value_failed(self, characteristic, error):
        self.append_safely("logs", "Error writing value: {}".format(error))

    def characteristic_write_value_succeeded(self, characteristic):
        self.message_sent = True

    def write(self, value):
        if self.write_characteristic is None:
            self.append_safely(
                "logs",
                "[{}] Can't send message '{}' ({})".format(
                    self.mac_address,
                    value,
                    "no write characteristic found"
                )
            )
            return

        self.message_sent = False
        self.append_safely(
            "logs",
            "[{}] Sending message: {}".format(
                self.mac_address,
                value
            )
        )
        self.write_characteristic.write_value(value.encode())

    def is_setup(self):
        return self.setup
