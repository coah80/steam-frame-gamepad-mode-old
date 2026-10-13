# Finding where the controller input goes

Use this when the person presses buttons and the app does nothing. The goal is to locate the input on one of three paths: the virtual gamepad, the app's X display, or nowhere (laser mode / dashboard).

## Record every path at once

Start these on the Frame (over SSH), then have the person in the headset bring the app to the front and press every control on both controllers, about a second apart: A, B, X, Y, d-pad all four ways, both sticks, bumpers, triggers.

1. **All input devices**: [`../tools/record-input.py`](../tools/record-input.py) logs key and button events, stick moves, triggers and d-pad hats from every `/dev/input/event*` device to `/tmp/input-events.log`, picking up devices Steam recreates. Copy it over and run it detached so it outlives the SSH session (its docstring has the commands).
2. **The app's display**: games run on gamescope's Xwayland `DISPLAY=:1` (Steam's own UI is `:0`). `systemd-run --user --collect --setenv=DISPLAY=:1 sh -c "timeout 300 xinput test-xi2 --root > /tmp/x1-events.log"`. Decode: `RawKeyPress`/`KeyPress` `detail` is the X keycode (evdev code + 8), `ButtonPress` `detail` the mouse button (4/5 = wheel).
3. **Steam's controller config**: `grep -a "Queueing activation\|uses xinput" ~/.local/share/Steam/logs/controller.txt` shows which app's controller config is active (769 = Steam's UI).
4. **The app itself**: a debug switch that logs the gamepads the app sees and each key it translates.

## Reading the result

- Keys and mouse on `:1`, nothing on the virtual pad: the controllers are in gamepad mode with Steam's **keyboard layout**. Build or fix the **bridge** (`../GUIDE.md`, `app-types.md`).
- Events on the virtual Xbox pad (`28de:11ff`): the app has a gamepad layout. Read it with the Gamepad API / SDL / evdev, standard mapping.
- Nothing anywhere: the controllers are lasers or the dashboard has focus. Close the dashboard (system button) with the app's panel in front, then press again; if the panel shows "Press A For Gamepad Mode", press A. Background: `steamvr-modes.md`.

## Seeing what the person sees

The Frame exposes the headset view as a V4L2 webcam: `ffmpeg -f v4l2 -i /dev/video99 -frames:v 1 /tmp/view.png` (service `steamvr-v4l2cam`). It is black or flat dark blue while nobody wears the headset, and shows passthrough, panels and dashboard while worn.

## SSH pitfalls on the Frame

- `pkill -f <pattern>` also matches the SSH shell whose command line contains the pattern, killing your own session (exit 255, broken pipes). Put the logic in a script file, or match a pattern that cannot appear in your command.
- Long multi-line Python inside `ssh '...'` gets mangled by quoting; copy a script over with `scp` and run it.
- A Chromium child keeps an inherited stdout pipe open after `timeout` kills the parent, so `subprocess.run(capture_output=True)` hangs. Write output to a file and kill the process group (`start_new_session=True`, `os.killpg`).
