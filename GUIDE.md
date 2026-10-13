# Steam Frame: controller input for flat apps

You are making a flat (non-VR) Linux app on the Valve Steam Frame respond to the Frame's controllers. Read the model first: most failed attempts assume the controllers arrive as a gamepad. For a non-Steam app they arrive as a **keyboard**.

Observed on one Steam Frame on 2026-10-13 (SteamOS, kernel 6.18, aarch64, the SteamVR bundled in `/opt/steamvr`) with an Electron 44 app added as a non-Steam game and launched from Steam in VR. Working reference implementation: [coah80/frametube](https://github.com/coah80/frametube). Where something here was not run on a device it says **untested**.

## The model

The Frame is an aarch64 SteamOS headset. A flat app launched from Steam runs under gamescope (Xwayland, games get `DISPLAY=:1`) and is shown on a SteamVR dashboard panel (overlay key `valve.steam.desktopgame.<appid>`). Each controller is in one of two modes, per hand:

- **Laser mode**: the controller pointing at a panel is a laser mouse. SteamVR's `/actions/lasermouse` set takes its buttons and its stick scrolls the panel; none of it reaches the app as controller input.
- **Gamepad mode**: Steam Input drives the app with the controller layout Steam assigned to it. For a **non-Steam shortcut** that layout is Steam's **keyboard layout**, "Keyboard (WASD) and Mouse" (`controller_base/templates/wasd.vdf`).

Observed: with the app's panel in front and the dashboard closed, every press arrived as **X11 key and mouse events** on the app's display, and nothing on Steam's virtual Xbox pad (`28de:11ff`, "Microsoft X-Box 360 pad 0"), which exists and the app can open but which received no events. So an app that waits for a gamepad sees nothing. The fix is a **bridge** inside the app that turns the keyboard layout's keys into the input the app wants.

The keyboard layout, what each control sends:

| Control | Sends | X keycode |
|---|---|---|
| left stick up / left / down / right | `w` / `a` / `s` / `d` (key repeat while held, diagonals press two) | 25 / 38 / 39 / 40 |
| left stick click | `Shift_L` (held: digits arrive shifted, `1` as `!`) | 50 |
| d-pad up / right / down / left | `1` / `2` / `3` / `4` | 10 / 11 / 12 / 13 |
| A / B / X / Y | `space` / `e` / `r` / `f` | 65 / 26 / 27 / 41 |
| menu / view | `Tab` / `Escape` | 23 / 9 |
| left / right bumper | mouse wheel down / up | buttons 5 / 4 |
| left / right trigger | right / left mouse button | buttons 3 / 1 |
| right stick | mouse pointer, click = `e` (same as B) | |
| back grips (if present) | left `c`, right `r` (same as X) | |

How this was established and the full template: [`reference/steam-keyboard-layout.md`](reference/steam-keyboard-layout.md). SteamVR's laser/gamepad switching and `preferGamepadMode`: [`reference/steamvr-modes.md`](reference/steamvr-modes.md).

## Steps

1. **Find what the app reads**: key events (which `event.key` / codes / scancodes), the Gamepad API, SDL game controllers, evdev. For a web app, search its JavaScript for `keydown`, key names and `getGamepads`. YouTube's TV app (youtube.com/tv), for example, reads only `event.key` `ArrowUp/Down/Left/Right`, `Enter`, `Escape`/`GoBack`, `Backspace`. Done when you have the exact list of inputs the app acts on, and you know which branch of [`reference/app-types.md`](reference/app-types.md) applies (keys, Gamepad API only, native/SDL).

2. **Write the bridge as a pure mapping** from keyboard-layout keys to the app's inputs, separate from the plumbing so it is unit-testable. Match the **physical** key (`input.code` in Electron, the scancode in SDL), never the character, so Shift from the stick click can't break the d-pad. Translate key up as well as key down, leave alone keys the app already understands (`Escape`) and anything with Ctrl/Alt/Meta, and pass everything through while a text field has focus. [`examples/steam-keys.js`](examples/steam-keys.js) (tests: `node --test examples/steam-keys.test.js`) is a version of FrameTube's mapping. Done when every control in the table has a target or a written "unmapped", and tests cover each mapped one plus the Shift case.

3. **Wire it in before the app sees the key**, following your branch in [`reference/app-types.md`](reference/app-types.md). For key-reading Electron apps: `before-input-event`, `preventDefault()`, then `webContents.sendInputEvent`, which produces **trusted** events. Synthetic DOM events (`dispatchEvent(new KeyboardEvent(...))`, `isTrusted=false`) are ignored by many apps, YouTube's TV app included. Keep the app's gamepad path too: it takes over if the user switches the app to a gamepad layout in Steam. Done when the wiring compiles and the raw keyboard-layout keys can no longer reach the app.

4. **Prove it off the device** with real X key events, the kind Steam produces: run the app on Xvfb and press keys with [`tools/xtest-keys.py`](tools/xtest-keys.py). Log what the app receives. Done when each mapped key arrives as its translated input (trusted, for web content) and the raw key does not arrive.

5. **Make it start under Steam** (Chromium/Electron apps; other apps only if they crash at start under Steam). Steam launches games with its overlay in `LD_PRELOAD` and its runtime's libraries in `LD_LIBRARY_PATH`; Chromium with both dies at start (`Zygote process exited prematurely`). Start the real binary through a launcher that drops those two variables, and leave Electron's setuid `chrome-sandbox` out of the build. Details, and why FrameTube's launcher is a static binary rather than a shell script: [`reference/chromium-on-frame.md`](reference/chromium-on-frame.md). Done when the app, launched from the Steam library on the Frame, stays running with no zygote error in its log.

6. **Prove it on the device.** Add a debug switch that logs every translated key (FrameTube: `FRAMETUBE_DEBUG=1`), get the app onto the Frame and into Steam (FramePort's "Add a Linux app" does both, or copy the folder over SSH and add the launcher as a non-Steam game), launch it from the library, and have the person in the headset press every control with the app's panel in front and the dashboard closed (system button toggles the dashboard). Done when the log shows each pressed control's translated input and the app visibly reacts. If presses go nowhere, follow [`reference/debugging.md`](reference/debugging.md). If you have no access to a Frame, stop after step 4 and hand over the build, the debug switch, and this step as the test for the person who has one.

## Gotchas (observed on the device)

- `app.commandLine.appendSwitch('no-sandbox')` in Electron's main script is too late: the sandbox and zygote start before any JavaScript runs. Anything that must happen before Chromium starts belongs in the launcher.
- Steam's `AppError_16` ("WaitingPrevProcess") on launch meant an earlier session was still alive. FramePort's `launch.sh` launchers trap `SIGTERM`, so a leftover one survived `kill`: end it with `kill -9`, along with its `reaper SteamLaunch AppId=<id>` parent.
- On the test Frame Steam dropped non-Steam entries from `shortcuts.vdf` on every restart and kept only "Devkit Game: <name>" entries, which Steam's devkit interface (`steam://devkit-1/.../create-shortcut`) adds. If the app vanishes from the library, FramePort re-adds it that way when you press Play.
- Desktop distros that block unprivileged user namespaces (Ubuntu 23.10+) need `--no-sandbox` for Electron; SteamOS did not.

FramePort ([spoopyghosty0/frameport](https://github.com/spoopyghosty0/frameport)) is a PC app that installs Quest games, Android apps and Linux apps on the Frame and adds them to Steam; it is optional here.
