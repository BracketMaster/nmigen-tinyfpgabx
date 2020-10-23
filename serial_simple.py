"""
Forms a simple loopback using Luna.
"""

from nmigen              import Elaboratable, Module

from luna                import top_level_cli
from luna.full_devices   import USBSerialDevice
from luna.gateware.stream import StreamInterface
from luna.gateware.platform.tinyfpga    import TinyFPGABxPlatform


class Serial(Elaboratable):
    def __init__(self):
        self.rx = StreamInterface()
        self.tx = StreamInterface()

    def elaborate(self, platform):
        m = Module()

        # Generate our domain clocks/resets.
        m.submodules.car = platform.clock_domain_generator()

        # Create our USB-to-serial converter.
        ulpi = platform.request(platform.default_usb_connection)
        m.submodules.usb_serial = usb_serial = \
                USBSerialDevice(bus=ulpi, idVendor=0x16d0, idProduct=0x0f3b)
        
        # connect peripherals
        m.d.comb += usb_serial.rx.connect(self.rx)
        m.d.comb += self.tx.connect(usb_serial.tx)

        # ... and always connect by default.
        m.d.comb += usb_serial.connect.eq(1)

        return m

class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.submodules.Serial = serial = Serial()
        m.d.comb += serial.rx.connect(serial.tx)
        return m

if __name__ == "__main__":
    top = Top()
    platform = TinyFPGABxPlatform()
    platform.build(top, do_program=True)
