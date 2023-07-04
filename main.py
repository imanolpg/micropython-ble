import ubluetooth
import time


# custom BLE server
class BLE:
    def __init__(self):
        self.name = "Awesome BLE server"
        self.ble = ubluetooth.BLE()
        self.device_connected = (
            False  # variable for controlling if a device has logged in
        )

        # save the UUIDs for the service and the characteristics
        self.SERVICE_1_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
        self.CHARACTERISTIC_1_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
        self.CHARACTERISTIC_2_UUID = "a2bdef65-f783-490d-b6ed-5ec887c85958"

        # the handlers need to be stored because a gatt notify will be made
        # the characteristic handle is needed
        self.service_1_handler = None
        self.characteristic_1_handler = None
        self.characteristic_2_handler = None

        self.ble.active(True)
        self.ble.irq(self.ble_irq)  # callback function when a bluetooth event is made
        self.register()  # create the service and the characteristics
        self.advertiser()  # show the bluetooth device to others device

    # callback function for bluetooth events
    def ble_irq(self, event, data):
        if event == 1:  # device connected
            print("Device connected")
            self.device_connected = True
        elif event == 2:  # device disconnected
            print("Device disconnected")
            self.device_connected = False
            self.advertiser()  # if a device has been disconnected the bluetooth server has to be shown to others device
        elif event == 3:  # a new message has been received
            # in order to check which characteristic is receiving the information, the second element
            # of the data tuple has to be the same as the characteristic handler
            if data[1] == self.characteristic_1_handler:
                print("Message in characteristic 1 received")
                try:
                    buffer = self.ble.gatts_read(
                        self.characteristic_1_handler
                    )  # read the data
                    message = buffer.decode(
                        "UTF-8"
                    ).strip()  # decode the data to string. This depends on the format the information is being sended
                    print(f'Message: {message}')
                except:
                    print("Error when converting value from characteristic 1")

            elif data[1] == self.characteristic_2_handler:
                print("Message in characteristic 2 received")
                try:
                    buffer = self.ble.gatts_read(
                        self.characteristic_2_handler
                    )  # read the data
                    message = buffer.decode(
                        "UTF-8"
                    ).strip()  # decode the data to string. This depends on the format the information is being sended
                    print(f'Message: {message}')
                except:
                    print("Error when converting value from characteristic 2")

    # create the services and the characteristics and add them to the ble
    def register(self):
        # first create the characteristics
        characteristic_1 = (
            ubluetooth.UUID(self.CHARACTERISTIC_1_UUID),
            ubluetooth.FLAG_WRITE | ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY,
        )
        characteristic_2 = (
            ubluetooth.UUID(self.CHARACTERISTIC_2_UUID),
            ubluetooth.FLAG_WRITE | ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY,
        )

        # second add the characteristics to a service
        self.service_1_handler = (
            ubluetooth.UUID(self.SERVICE_1_UUID),
            (characteristic_1, characteristic_2),
        )
        # as one or more services can be created we need a tuple or list with all the services
        services = (self.service_1_handler,)

        # add the services to the ble and collect the characteristic handlers to send data
        (
            (self.characteristic_1_handler, self.characteristic_2_handler),
        ) = self.ble.gatts_register_services(services)

        print("Registers done")

    # show the BLE server to other devices
    def advertiser(self):
        name = bytes(self.name, "UTF-8")
        self.ble.gap_advertise(
            100,
            bytearray("\x02\x01\x02", "utf-8")
            + bytearray((len(name) + 1, 0x09), "utf-8")
            + name,
        )
        print("Device advertised")

    # send a new message to a characteristic.
    # as we have to know the desired characteristic to use the correct handler a param
    # for knowing the characteristic has been included
    # in this example only strings are being sent. In order to send other data like 
    # floats use other data types like UINT 8
    def send(self, characteristic, data):
        if self.device_connected:
            if characteristic == 1:
                self.ble.gatts_notify(0, self.characteristic_1_handler, data)
                print(f"Value sent to characteristic 1: {data}")
            elif characteristic == 2:
                self.ble.gatts_notify(0, self.characteristic_2_handler, data)
                print(f"Value sent to characteristic 2: {data}")
        else:
            print("No device connected")


# main function
def main():

    # create ble server
    ble = BLE()

    while True:
        # broadcast the data over bluetooth
        ble.send(1, "Characteristic 1")
        ble.send(2, "Characteristic 2")

        time.sleep(2)  # wait 2 seconds


if __name__ == "__main__":
    main()
