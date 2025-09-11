/**
 * @jest-environment jsdom
 *  Tests delete_modal.js: ensures the confirmation modal shows correctly and submits the targeted form
 */

beforeEach(() => {
  document.body.innerHTML = `
    <div id="confirmDeleteModal">
      <button id="confirmDeleteSubmit">Confirm</button>
      <div id="confirmDeleteMessage"></div>
      <div id="confirmDeleteDetails"></div>
    </div>
    <form id="f1"></form>
    <button id="trigger"
            data-form="f1"
            data-message="Are you sure?"
            data-details="This action can't be undone."></button>
  `;

  // Minimal Bootstrap
  global.bootstrap = { Modal: class { static getInstance(){return null} hide(){} } };

  // Load the module, but it waits for DOMContentLoaded to attach handlers
  require('../delete_modal.js');

  // Let the module initialize
  document.dispatchEvent(new Event('DOMContentLoaded', { bubbles: true }));
});

test('confirm button submits the correct form', () => {
  const modal = document.getElementById('confirmDeleteModal');
  const trigger = document.getElementById('trigger');
  const form = document.getElementById('f1');
  const submitSpy = jest.spyOn(form, 'submit').mockImplementation(() => {});

  // Simulate Bootstrap opening with a relatedTarget
  const showEvt = new Event('show.bs.modal', { bubbles: true });
  showEvt.relatedTarget = trigger;
  modal.dispatchEvent(showEvt);

  // Click confirm
  document.getElementById('confirmDeleteSubmit').click();

  expect(submitSpy).toHaveBeenCalled();
});
