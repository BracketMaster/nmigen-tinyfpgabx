# Some TinyFPGABX Experiments in nMigen

 - blinky
 - USB Serial UART

# Dependencies
 - [NextPnr](https://github.com/YosysHQ/nextpnr)
You'll want to build nextPNR with support for at
least the ice40.
 - [yosys](https://github.com/YosysHQ/yosys)

You may wish to first create a Python
virtual environment since there are a lot
of Python dependencies.

```
cd ~/.virtualenvs
python3 -m venv tinyfpga
source tinyfpga/bin/activate
```

```
cd tinyfpgabx_experiments
pip3 install -r requirements.txt
```
# Using

## Blinky

Running ``python3 blinky.py`` should start blinking the
LED on the FPGA.

![](doc/fpga.gif)

## Luna ACM Serial UART

```
python3 acm_serial.py
python3 driver.py
```

The serial link is configured in acm_serial.py
to add one to the sent character and return it.

So ``driver.py`` send ``a`` and receives back ``b``
which it prints out to the terminal.