from nmigen import *
from nmigen_boards.tinyfpga_bx import *


class Blinky(Elaboratable):
    def elaborate(self, platform):
        user_led = platform.request("led", 0)
        counter  = Signal(23)

        m = Module()
        m.d.sync += counter.eq(counter + 1)
        m.d.comb += user_led.o.eq(counter[-1])
        return m


if __name__ == "__main__":
    platform = TinyFPGABXPlatform()
    platform.build(Blinky(), do_program=True)