"""Logs key/button events, stick moves past a dead zone, trigger pulls and d-pad hats from every /dev/input/event*
device to /tmp/input-events.log for SECONDS (default 300), re-scanning every 2 s for devices Steam creates or
recreates (its virtual pad). On the Frame the steamos user can read these devices (input group / ACLs); elsewhere run
it as a member of the input group. Copy it over and run it detached so it outlives the SSH session:
    scp record-input.py steamos@<frame>:/tmp/ && ssh steamos@<frame> systemd-run --user --collect python3 /tmp/record-input.py
    optional: python3 record-input.py 600   (seconds)"""
import os
import re
import select
import struct
import sys
import time

LOG = "/tmp/input-events.log"
SECONDS = int(sys.argv[1]) if len(sys.argv) > 1 else 300
FMT = "llHHi"  # struct input_event on 64-bit Linux
SIZE = struct.calcsize(FMT)
EV_KEY, EV_ABS = 1, 3
STICK_AXES = (0, 1, 3, 4)  # ABS_X/Y, ABS_RX/RY
TRIGGER_AXES = (2, 5)  # ABS_Z/RZ
HAT_AXES = (16, 17)  # ABS_HAT0X/Y: the Xbox pad's d-pad
# trigger/hat codes only from gamepads: a Frame headset sensor reports a busy ABS code 2 of its own
PAD_NAMES = ("pad", "controller", "joystick", "gamepad")
DEAD_ZONE = 8000


def is_pad(name):
    return any(word in name.lower() for word in PAD_NAMES)


def stamp():
    return time.strftime("%H:%M:%S")


def devices():
    """(path, name) of every input device with an event node."""
    for block in open("/proc/bus/input/devices").read().split("\n\n"):
        ev = re.search(r"event(\d+)", block)
        name = re.search(r'N: Name="([^"]*)"', block)
        if ev:
            yield "/dev/input/event" + ev.group(1), name.group(1) if name else "?"


def main():
    out = open(LOG, "a", buffering=1)
    out.write(stamp() + " recorder started\n")
    fds, names, failed = {}, {}, set()
    end = time.time() + SECONDS
    last_scan = 0.0
    while time.time() < end:
        if time.time() - last_scan > 2:
            last_scan = time.time()
            for path, name in devices():
                if path in fds.values() or path in failed:
                    continue
                try:
                    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                except OSError as e:
                    failed.add(path)  # reported once, not every scan
                    out.write("%s %s (%s): %s\n" % (stamp(), path, name, e))
                    continue
                fds[fd], names[fd] = path, name
                out.write("%s opened %s (%s)\n" % (stamp(), path, name))
        ready, _, _ = select.select(list(fds), [], [], 1)
        for fd in ready:
            try:
                data = os.read(fd, SIZE * 64)
            except BlockingIOError:
                continue
            except OSError:
                out.write("%s lost %s\n" % (stamp(), fds.pop(fd)))
                os.close(fd)
                continue
            for i in range(0, len(data) - SIZE + 1, SIZE):
                _s, _u, typ, code, value = struct.unpack_from(FMT, data, i)
                if typ == EV_KEY and value != 2:  # 2 = autorepeat
                    out.write("%s %s KEY code=%d value=%d (%s)\n" % (stamp(), fds[fd], code, value, names[fd]))
                elif typ == EV_ABS and ((code in STICK_AXES and abs(value) >= DEAD_ZONE) or (is_pad(names[fd]) and (
                        (code in TRIGGER_AXES and value > 0) or code in HAT_AXES))):
                    out.write("%s %s ABS code=%d value=%d (%s)\n" % (stamp(), fds[fd], code, value, names[fd]))
    for fd in fds:
        os.close(fd)
    out.write(stamp() + " recorder stopped\n")


if __name__ == "__main__":
    main()
