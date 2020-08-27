import usb.core
import usb.util

# find our device
dev = usb.core.find(idVendor=0x16d0, idProduct=0x0f3b)

# was it found?
if dev is None:
    raise ValueError('Device not found')

# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()
intf = cfg[(1,0)]
####

out = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

#####

inn = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN)

msg = 'hi there'
out.write(msg)

buf = []
ret = inn.read(10)
print(" ==== SENT PACKET ==== ")
print(msg)
print()
print(" ==== RETURNED PACKET ==== ")
print(" ==== BY INT ==== ")
print(list(ret))
print(" ==== BY BYTE ==== ")
print([format(val, '08b') for val in list(ret)])
print(" ==== AS STRING ==== ")
print(ret.tostring().decode("utf-8"))