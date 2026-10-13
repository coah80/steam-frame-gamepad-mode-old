# SteamVR laser mode and gamepad mode

Read from the SteamVR files on the Frame: the dashboard web UI (`/opt/steamvr/resources/webinterface/dashboard/*.js`), the compositor bindings for the Frame controller (`/opt/steamvr/drivers/frame_controller/resources/input/vrcompositor_bindings_frame_controller.json`), the defaults (`/opt/steamvr/resources/settings/default.vrsettings`) and strings in `vrclient.so`.

## Laser mode

While a controller's laser is on a panel, the compositor bindings apply:

- `/actions/lasermouse`: trigger and bumper = left click (and `LockMousePosition`), stick click = right click, left d-pad right = middle click, left d-pad left = back, left d-pad down = home, right X = middle click, right B = back, right A = home.
- `/actions/scroll_smooth` and `/actions/scroll_discrete`: either stick scrolls the panel. Reported in [ValveSoftware/SteamVR-for-Linux#1000](https://github.com/ValveSoftware/SteamVR-for-Linux/issues/1000): for a desktop app panel that scroll mostly never reaches the app, while the other (non-laser) controller's stick does arrive through the virtual pad when the app has a gamepad layout.
- `/actions/lasermouse_secondary`: trigger, grip or bumper on the other hand moves the laser to that hand.
- `/actions/quickmouse`: grip = `ActivateQuickMouse`. Tapping grip flips a laser-holding controller to gamepad input for a moment, then Steam returns it to the laser.
- `/actions/system`: system button click = toggle dashboard, double = room view, held = system chord.

`vrclient.so` carries per-hand behaviour flags `SystemBehaviorFlag_GamepadMode_Left`, `SystemBehaviorFlag_GamepadMode_Right` and `SystemBehaviorFlag_LaserMouse`. The default setting `dashboard/modalGamepadAndLaser: true` makes the two exclusive.

## Gamepad mode

The dashboard offers gamepad mode on a panel only when the panel `supportsGamepadFocus`:

```
supportsSteamInput   = gamepadFocusAllowed && !!componentProps.steamInputAppID
supportsVRInput      = gamepadFocusAllowed && !!componentProps.vrClientPID
supportsGamepadFocus = supportsSteamInput || supportsVRInput
```

When it does, the panel shows "Press %1$s For Gamepad Mode" / an "Enter Gamepad Mode" button. Gamepad button 1 or 2 (A/B) on that prompt runs `HandleEnterGamepadModeButtonClick`: it pushes input focus to the panel and hides or dims (diminished state) the dashboard. When the panel does not support gamepad focus, a "gamepad input not supported" banner shows instead and the controllers stay lasers. Gamepad mode is also suppressed while streaming VR from a PC ("Gamepad input is not yet supported while streaming VR").

## preferGamepadMode

`dashboard/preferGamepadMode` (absent = off, not in the settings UI) makes the dashboard prefer gamepad focus for panels. Set it live and persist it:

```
/opt/steamvr/bin/linuxarm64/vrcmd --set-settings-bool dashboard.preferGamepadMode 1
/opt/steamvr/bin/linuxarm64/vrcmd --settings-bool dashboard.preferGamepadMode   # dashboard.preferGamepadMode=true
```

The argument is `section.key value` with `1`/`0` (`true` reads as 0, `section/key` is rejected). SteamVR writes `~/.config/openvr/config/steamvr.vrsettings` later; add `"preferGamepadMode": true` under `"dashboard"` there too so it survives a restart.

It does not change what a non-Steam app receives: in gamepad mode Steam Input still applies the app's assigned layout, the keyboard layout. Use the **bridge** either way.
