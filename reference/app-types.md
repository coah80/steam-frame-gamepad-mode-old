# Bridging by app type

Pick the branch that matches what the app reads (GUIDE.md step 1). Only the first branch has been run on a Frame; the others follow from the same input model and are marked untested.

## The app reads keys (web apps, Electron, most TV/media UIs) — tested

Map keyboard-layout keys to the app's keys and send them as trusted key events. Electron, in the main process:

```js
const { translate } = require('./steam-keys'); // examples/steam-keys.js
win.webContents.on('before-input-event', (event, input) => {
  const keyCode = translate(input, { typing: textFieldFocused });
  if (!keyCode) return;
  event.preventDefault();                                   // the raw w/a/s/d never reaches the page
  win.webContents.sendInputEvent({ type: input.type, keyCode }); // trusted, with the right event.key
});
```

`sendInputEvent` from inside the handler does not loop as long as no output key is also an input key. Track `textFieldFocused` from the page (a preload reporting `document.activeElement` is an `input`/`textarea`/contenteditable) if the app has real text fields; TV-style apps with their own on-screen keyboard don't need it.

## The app reads only the Gamepad API (Electron) — untested

Choose in this order:

1. If you own the app code, add key handling for the keyboard layout's keys next to the gamepad code. Simplest and testable.
2. Otherwise inject a virtual gamepad into the page: in a preload with `contextIsolation: false` (or `webFrame.executeJavaScript` into the main world), replace `navigator.getGamepads` with a function that returns the real pads plus one standard-mapping pad whose `buttons`/`axes` are driven by the layout keys (`Space` → button 0, `e` → 1, `r` → 2, `f` → 3, `1`-`4` → 12/15/13/14, `w a s d` → axes 0/1), with `connected: true`, `mapping: 'standard'` and a `timestamp` that changes on every update, and dispatch a `gamepadconnected` event once. Swallow the raw keys in `before-input-event` so the page doesn't also see them.
3. Or have the user switch the app's Steam controller layout to a gamepad template (below).

## Native games and SDL2 apps — untested

- SDL2 under gamescope uses the X11 driver (Xwayland). Handle `SDL_KEYDOWN`/`SDL_KEYUP` by **scancode** (`SDL_SCANCODE_W`, `SDL_SCANCODE_1`, `SDL_SCANCODE_SPACE` …), which ignores Shift like `input.code` does.
- SDL will likely enumerate Steam's virtual Xbox pad (`28de:11ff`) as a game controller that never sends events. A game that switches to "controller mode" when a pad is present must still accept keyboard input, or treat a pad with no input as absent.
- The mouse half of the layout (triggers = right/left click, bumpers = wheel, right stick = pointer) arrives as normal mouse events.
- Skip the Chromium launcher (GUIDE.md step 5) unless the game crashes at start under Steam; many native games rely on Steam's runtime libraries in `LD_LIBRARY_PATH`.
- The Frame is aarch64: build for arm64, or run an x86_64 build through FEX (FramePort sets this up).

## Switching the app's Steam layout to a gamepad — untested on the Frame

Steam lets you pick a controller layout per game, non-Steam shortcuts included (the game's controller settings, layout, a gamepad template). With a gamepad layout Steam Input should drive the virtual Xbox pad, and the app reads it with the Gamepad API / SDL / evdev using the standard mapping. It needs a manual step from every user and persists per Steam account. Confirm it with `tools/record-input.py`: presses must appear on the "Microsoft X-Box 360 pad" device. The bridge needs no setup, so prefer it and keep a gamepad path as a fallback.
