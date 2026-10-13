'use strict';

// node --test steam-keys.test.js
const test = require('node:test');
const assert = require('node:assert/strict');
const { translate } = require('./steam-keys');

const key = (code, extra = {}) => ({ type: 'keyDown', code, key: code.replace(/^(Key|Digit)/, '').toLowerCase(), ...extra });

test('left stick (WASD) and d-pad (1-4) become arrows', () => {
  assert.deepEqual(['KeyW', 'KeyA', 'KeyS', 'KeyD'].map((c) => translate(key(c))), ['Up', 'Left', 'Down', 'Right']);
  assert.deepEqual(['Digit1', 'Digit2', 'Digit3', 'Digit4'].map((c) => translate(key(c))), ['Up', 'Right', 'Down', 'Left']);
});

test('A (Space) selects, B (E) goes back, X (R) plays/pauses', () => {
  assert.equal(translate(key('Space')), 'Enter');
  assert.equal(translate(key('KeyE')), 'Escape');
  assert.equal(translate(key('KeyR')), 'MediaPlayPause');
});

test('with the stick clicked (Shift held) the d-pad still maps: "1" arrives as key "!"', () => {
  assert.equal(translate({ type: 'keyDown', code: 'Digit1', key: '!', shift: true }), 'Up');
  assert.equal(translate({ type: 'keyDown', code: 'KeyW', key: 'W', shift: true }), 'Up');
});

test('key up is translated too, so held keys are released', () => {
  assert.equal(translate({ type: 'keyUp', code: 'KeyD', key: 'd' }), 'Right');
});

test('typing in a text field passes keys through', () => {
  assert.equal(translate(key('KeyW'), { typing: true }), null);
});

test('keys the app understands, shortcuts and other events are left alone', () => {
  assert.equal(translate(key('Escape')), null);
  assert.equal(translate({ type: 'keyDown', code: 'ArrowUp', key: 'ArrowUp' }), null);
  assert.equal(translate(key('KeyW', { control: true })), null);
  assert.equal(translate({ type: 'char', code: 'KeyW', key: 'w' }), null);
  assert.equal(translate(null), null);
});
