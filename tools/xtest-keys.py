"""Presses keys on an X display through XTest: real X key events, like Steam's keyboard controller layout produces.
Use it to prove a bridge off the device: run the app on Xvfb, press the layout's keys, log what the app receives.

    Xvfb :99 -screen 0 1920x1080x24 &
    DISPLAY=:99 <start your app> &
    DISPLAY=:99 python3 xtest-keys.py 25 space s s e w     # wait 25 s for the app, then press each key
    (pip/uv package: python-xlib)

Key names are X keysym names: letters (w a s d e r f), digits (1 2 3 4), space, Escape, Tab, Shift_L.
A fullscreen Electron window took the keys without a window manager; for other apps make sure the window has focus."""
import sys
import time

from Xlib import X, XK, display
from Xlib.ext import xtest

if len(sys.argv) < 3:
    sys.exit(__doc__)
d = display.Display()
if not d.has_extension("XTEST"):
    sys.exit("the X server has no XTEST extension")
codes = []
for name in sys.argv[2:]:
    code = d.keysym_to_keycode(XK.string_to_keysym(name))
    if not code:
        sys.exit(f"unknown key name {name!r} (use X keysym names, e.g. space, Escape)")
    codes.append((name, code))
time.sleep(float(sys.argv[1]))
for name, code in codes:
    xtest.fake_input(d, X.KeyPress, code)
    d.sync()
    time.sleep(0.08)
    xtest.fake_input(d, X.KeyRelease, code)
    d.sync()
    print(f"xtest: pressed {name} (keycode {code})", flush=True)
    time.sleep(1.5)
