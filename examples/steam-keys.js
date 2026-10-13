'use strict';

// Steam on the Frame gives a non-Steam app its "Keyboard (WASD) and Mouse" controller layout
// (controller_base/templates/wasd.vdf): the controllers arrive as key presses, not as a gamepad. This maps those keys
// to the remote-control keys YouTube's TV app reads (event.key ArrowUp/Down/Left/Right, Enter, Escape). Swap the
// targets for whatever your app reads.
//
//   left stick  W A S D        -> arrows       A button  Space -> Enter (select)
//   d-pad       1 2 3 4        -> arrows       B button  E     -> Escape (back)
//   (1 up, 2 right, 3 down, 4 left)            X button  R     -> play/pause
// Escape (the controller's view button) already means back and is left alone. Y (F), menu (Tab), the back grips
// (C, R) and the mouse half of the layout (triggers, bumpers, right stick) are deliberately unmapped here.
//
// Matching is on the physical key (input.code, e.g. "KeyW", "Digit1"), not input.key: the left stick click holds
// Shift, and with Shift held the d-pad's "1" arrives as key "!".

const STEAM_KEYS = {
  KeyW: 'Up',
  KeyA: 'Left',
  KeyS: 'Down',
  KeyD: 'Right',
  Digit1: 'Up',
  Digit2: 'Right',
  Digit3: 'Down',
  Digit4: 'Left',
  Space: 'Enter',
  KeyE: 'Escape',
  KeyR: 'MediaPlayPause',
};

// Electron's before-input-event input -> the Electron key code to send instead, or null to leave the key alone.
// Keys with Ctrl/Alt/Meta held are never translated (shortcuts). Pass typing: false while a text field has focus,
// so a real or on-screen keyboard can still type w, a, s, d...
function translate(input, { typing = false } = {}) {
  if (typing || !input || (input.type !== 'keyDown' && input.type !== 'keyUp')) return null;
  if (input.control || input.alt || input.meta) return null;
  return Object.prototype.hasOwnProperty.call(STEAM_KEYS, input.code) ? STEAM_KEYS[input.code] : null;
}

module.exports = { STEAM_KEYS, translate };
