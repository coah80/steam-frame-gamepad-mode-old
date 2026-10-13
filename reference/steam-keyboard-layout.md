# Steam's keyboard layout for non-Steam apps

## What Steam assigns

A non-Steam shortcut on the Frame gets Steam Input's **"Keyboard (WASD) and Mouse"** template, the one in `~/.local/share/Steam/controller_base/templates/wasd.vdf`. Its bindings, as Steam ships them:

| Group | Source | Binding |
|---|---|---|
| four buttons | `button_diamond` | A `SPACE`, B `E`, X `R`, Y `F` |
| d-pad | `left_trackpad` (the d-pad on the Frame controller) | north `1`, east `2`, south `3`, west `4` |
| joystick (dpad mode, overlap on) | `joystick` (left stick) | north `W`, south `S`, east `D`, west `A`, click `LEFT_SHIFT` |
| absolute mouse | `right_trackpad` / right stick | pointer motion, click `E` |
| triggers | `left_trigger` / `right_trigger` | right / left mouse button |
| switches | bumpers | left = wheel down, right = wheel up |
| switches | `button_menu` / `button_escape` | `TAB` / `ESCAPE` |
| switches | back grips | left `C`, right `R` |

The stick works as a d-pad: a direction press is a key down, holding it gives key repeat, and diagonals press two keys at once (overlap). Expect key repeat to arrive as repeated key downs.

## How it was established

With an app in front and the person in the headset pressing every control, recording showed:

- Steam's controller log (`~/.local/share/Steam/logs/controller.txt`): "Controller 0 uses xinput : true (warmed config for app <appid>)" at launch, then "Queueing activation for controller: 0 app: …" alternating between `769` (Steam's own UI) and one other id while the dashboard and app took turns, never the shortcut's own app id.
- Every `/dev/input/event*` device, the virtual Xbox pad included: zero button or stick events from the presses (only an unrelated headset sensor on another device).
- `xinput test-xi2 --root` on `DISPLAY=:1`: key presses and mouse buttons/motion for every press. The keycodes (`X keycode = evdev code + 8`) match the template above.

## Gamepad mode the other way round

If the user changes the app's controller layout in Steam (controller settings for the game, a gamepad template), Steam Input drives the virtual Xbox pad instead and the Gamepad API / evdev path sees standard gamepad input. A bridge that handles both covers either choice.
