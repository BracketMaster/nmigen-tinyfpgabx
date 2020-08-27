"""
Demonstrates how to drive the signals on
the Serial link directly with a simple 
state machine.

Also forms a loopback, but holds packet
payloads in memory instead.

Note that all synchronous logic that interfaces
with the serial link must be in the ``usb``
domain.
"""

from nmigen import Module, Elaboratable, Signal
from nmigen import Array

from luna.gateware.stream import StreamInterface
from luna.full_devices import USBSerialDevice
from luna.gateware.platform.tinyfpga import TinyFPGABxPlatform


class InterfaceController(Elaboratable):
    def __init__(self):
        self.rx_serial = StreamInterface()
        self.tx_serial = StreamInterface()

    def elaborate(self, platform):
        m = Module()

        rx_serial = self.rx_serial
        tx_serial = self.tx_serial

        letters = Array([Signal(8) for _ in range(8)])
        counter = Signal(8)

        with m.FSM(domain="usb"):

            with m.State('FIRST'):
                m.d.comb += self.rx_serial.ready.eq(1)

                with m.If(rx_serial.valid & rx_serial.first):
                    m.d.usb += letters[counter].eq(rx_serial.payload)
                    # if payload is both the first and last in packet
                    with m.If(rx_serial.last):
                        m.d.usb += counter.eq(0)
                        m.next = 'SEND'
                    # if the payload is only the first in packet
                    with m.Else():
                        m.d.usb += counter.eq(counter + 1)
                        m.next = 'BODY'
            
            with m.State('BODY'):
                m.d.comb += self.rx_serial.ready.eq(1)
                with m.If(rx_serial.valid):
                    m.d.usb += letters[counter].eq(rx_serial.payload)
                    with m.If(rx_serial.last):
                        m.d.usb += counter.eq(0)
                        m.next = 'SEND'
                    with m.Else():
                        m.d.usb += counter.eq(counter + 1)

            
            with m.State('SEND'):
                with m.If(tx_serial.ready):
                    m.d.comb += tx_serial.valid.eq(1)
                    m.d.comb += tx_serial.payload.eq(letters[counter])

                    with m.If(counter == 0):
                        m.d.comb += tx_serial.first.eq(1)

                    with m.If(counter == 7):
                        m.d.comb += tx_serial.last.eq(1)
                        m.d.usb += counter.eq(0)
                        m.next = 'FIRST'
                    with m.Else():
                        m.d.usb += counter.eq(counter + 1)
        
        return m

class SerialLink(Elaboratable):
    def __init__(self, sim, max_packet_size):
        self.rx = StreamInterface()
        self.tx = StreamInterface()

        # parameters
        self.sim = sim
        self.max_packet_size = max_packet_size

    def elaborate(self, platform):
        m = Module()

        if not self.sim:
            # Generate our domain clocks/resets.
            m.submodules.car = platform.clock_domain_generator()

            # Create our USB-to-serial converter.
            ulpi = platform.request(platform.default_usb_connection)
            m.submodules.usb_serial = usb_serial = \
                    USBSerialDevice(bus=ulpi, idVendor=0x16d0,
                            idProduct=0x0f3b, max_packet_size=self.max_packet_size)
            
            # connect peripherals
            m.d.comb += self.rx.connect(usb_serial.rx)
            m.d.comb += usb_serial.tx.connect(self.tx)

            # ... and always connect by default.
            m.d.comb += usb_serial.connect.eq(1)

        return m

class Top(Elaboratable):
    def __init__(self, sim, max_packet_size):
        # instantiate components
        self.serial_link = SerialLink(sim=sim, max_packet_size=max_packet_size)
        self.interface_controller = InterfaceController()
    
    def elaborate(self, platform):
        m = Module()
        
        # attach components
        m.submodules.serial_link = serial_link = self.serial_link
        m.submodules.interface_controller = interface_controller \
            = self.interface_controller
        
        # (serial link) <> (interface controller)
        m.d.comb +=  interface_controller.rx_serial.connect(serial_link.rx)
        m.d.comb += serial_link.tx.connect(interface_controller.tx_serial)

        return m

if __name__ == "__main__":
    from luna.gateware.platform.tinyfpga import TinyFPGABxPlatform
    top = Top(sim=False, max_packet_size=64)
    platform = TinyFPGABxPlatform()
    platform.build(top, do_program=True)