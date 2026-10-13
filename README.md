# steam frame gamepad mode docs

notes on how controller input actually reaches flat (non-vr) apps on the steam frame, written so an ai model can read them and get it right way faster instead of spending hours finding out the hard way like i did. the electron/web app path is tested on a real frame, the rest is marked untested where it is.

the short version, a non-steam app on the frame doesnt get a gamepad. steam gives it its "keyboard (wasd) and mouse" layout, so your controllers show up as keys like w a s d, 1 2 3 4, space, e. steam's virtual xbox pad exists but gets nothing. the fix is a small bridge in the app that turns those keys into whatever the app wants. theres also a chromium/electron crash when launching from steam that these cover.

## using it with a model

paste this:

> read https://github.com/coah80/steam-frame-gamepad-mode/blob/main/GUIDE.md and the files it links, then make `<your app>` work with the steam frame controllers. follow the steps, each one says when its done.

or clone the repo next to your project, `AGENTS.md` points coding agents at the guide.

## whats in here

- `GUIDE.md`, the model + the steps, start here
- `reference/`, the deeper stuff the guide links to: steam's keyboard layout, what to do per app type (key apps, gamepad-only apps, native/sdl games), steamvr's laser vs gamepad mode, chromium on the frame, debugging where input goes
- `tools/record-input.py`, logs every input device on the frame, `tools/xtest-keys.py`, presses real x keys for testing off the device
- `examples/steam-keys.js`, the key mapping [FrameTube](https://github.com/coah80/frametube) uses, with tests

FrameTube is the working app this all came from, youtube's tv app as a flat app on the frame.

the tested parts were tested on a real steam frame in oct 2026. steamos and steamvr change, so if something doesnt match, check the files the reference points at on the device itself.

## license

MIT
