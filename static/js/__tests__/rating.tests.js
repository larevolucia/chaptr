/**
 * @jest-environment jsdom
 *
 * This test runs in a browser-like DOM (via jsdom) so we can interact
 * with document/window, dispatch events, and test UI behaviors.
 */

const fs = require('fs');   // Node API to read files from disk
const path = require('path'); // Node API to build cross-platform file paths

// Use Jest's fake timers so we can fast-forward debounce delays instantly.
jest.useFakeTimers();

beforeEach(() => {
  // 1) Minimal DOM that rating.js expects
  document.body.innerHTML = `
    <form id="rating-form-123">
      <input type="radio" name="rating" value="3">
      <input type="radio" name="rating" value="4">
    </form>
  `;

  // 2) Load rating.js into the DOM as if it were included by a <script> tag
  const scriptText = fs.readFileSync(
    path.join(__dirname, '..', 'rating.js'),
    'utf8'
  );
  const scriptEl = document.createElement('script');
  scriptEl.text = scriptText;
  document.head.appendChild(scriptEl);

  // 3) Mock the standards-based form submission method so we can assert on it.
  window.HTMLFormElement.prototype.requestSubmit = jest.fn();
});

test('debounces rating submit to a single request', () => {
  // Grab both radio inputs (simulate clicking different stars quickly)
  const [r3, r4] = document.querySelectorAll('input[name="rating"]');

  // Fire two quick change events
  r3.checked = true;
  r3.dispatchEvent(new Event('change', { bubbles: true }));
  r4.checked = true;
  r4.dispatchEvent(new Event('change', { bubbles: true }));
  // NOTE: { bubbles: true } makes the event bubble up the DOM like a real browser event.

  // Jump time forward past the debounce window so the submit trigger runs
  jest.advanceTimersByTime(1000);

  // Because of debouncing, only ONE submit should have been requested
  expect(HTMLFormElement.prototype.requestSubmit).toHaveBeenCalledTimes(1);
});

test('removeRating posts rating=0 and submits form', () => {
  const form = document.getElementById('rating-form-123');

  // Spy on this specific form's requestSubmit as well
  const submitSpy = jest
    .spyOn(form, 'requestSubmit')
    .mockImplementation(() => {});

  // removeRating was declared at top level in rating.js,
  // so after injecting the script it exists on window.*
  expect(typeof window.removeRating).toBe('function');

  // Call the helper: it should add a hidden input with rating=0 and submit the form
  window.removeRating('123');

  // Assert hidden input exists and has the expected value
  const hidden = form.querySelector('input[type="hidden"][name="rating"]');
  expect(hidden).toBeTruthy();
  expect(hidden.value).toBe('0');

  // And the form was submitted
  expect(submitSpy).toHaveBeenCalled();
});