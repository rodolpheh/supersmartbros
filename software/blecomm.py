import gatt


READ_CHARACTERISTIC = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
WRITE_CHARACTERISTIC = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"


class BLEComm(gatt.Device):
    def __init__(
            self, logs, lock, debug, *args,
            on_message_received=None,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = logs
        self.lock = lock
        self.debug = debug
        self.on_message_received = on_message_received

        self.message_sent = True
        self.write_characteristic = None
        self.setup = False

    def append_log(self, log):
        with self.lock:
            if self.debug:
                print(log)
            self.logs.append(log)
        return

    def connect_succeeded(self):
        super().connect_succeeded()
        self.append_log("[{}] Connected".format(self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        self.append_log(
            "[{}] Connection failed: {}".format(self.mac_address, str(error))
        )

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        self.append_log("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        self.append_log(
            "[{}] Resolved services".format(self.mac_address)
        )

        for service in self.services:
            self.append_log(
                "[{}]\tService [{}]".format(
                    self.mac_address,
                    service.uuid
                )
            )

            for characteristic in service.characteristics:
                self.append_log(
                    "[{}]\t\tCharacteristic [{}]".format(
                        self.mac_address,
                        characteristic.uuid
                    )
                )

                # Register the read characteristic when found
                if (characteristic.uuid == READ_CHARACTERISTIC):
                    characteristic.read_value()
                    characteristic.enable_notifications()

                # Register the write characteristic when found
                if (characteristic.uuid == WRITE_CHARACTERISTIC):
                    self.write_characteristic = characteristic

                for descriptor in characteristic.descriptors:
                    try:
                        self.append_log(
                            "[{}]\t\t\tDescriptor [{}] ({})".format(
                                self.mac_address,
                                descriptor.uuid,
                                descriptor.read_value()
                            )
                        )
                    except AttributeError as err:
                        self.append_log(
                            "[{}]\t\t\tDescriptor [{}] ({})".format(
                                self.mac_address,
                                descriptor.uuid,
                                err
                            )
                        )

        self.setup = True

    def descriptor_read_value_failed(self, descriptor, error):
        self.append_log('descriptor_value_failed')

    def characteristic_value_updated(self, characteristic, value):
        self.append_log(
            "[{}] Received: {}".format(self.mac_address, value)
        )
        if self.on_message_received is not None:
            self.on_message_received(value)

    def characteristic_write_value_failed(self, characteristic, error):
        self.append_log("Error writing value: {}".format(error))

    def characteristic_write_value_succeeded(self, characteristic):
        self.message_sent = True

    def write(self, value):
        self.write_raw(value.encode())

    def write_raw(self, value):
        if self.write_characteristic is None:
            self.append_log(
                "[{}] Can't send message '{}' ({})".format(
                    self.mac_address,
                    value,
                    "no write characteristic found"
                )
            )
            return

        self.message_sent = False
        self.append_log(
            "[{}] Sending: {}".format(
                self.mac_address,
                value
            )
        )
        self.write_characteristic.write_value(value)

    def is_setup(self):
        return self.setup
