document.addEventListener('DOMContentLoaded', function () {
  var modalEl = document.getElementById('confirmDeleteModal');
  if (!modalEl) return;

  var submitBtn = modalEl.querySelector('#confirmDeleteSubmit');
  var msgEl = modalEl.querySelector('#confirmDeleteMessage');

  // Store the target form id on the modal element
  modalEl.addEventListener('show.bs.modal', function (event) {
    var trigger = event.relatedTarget;
    if (!trigger) return;

    var formId  = trigger.getAttribute('data-form');   // REQUIRED
    var message = trigger.getAttribute('data-message'); // optional

    if (formId) modalEl.dataset.formId = formId;
    if (message && msgEl) msgEl.textContent = message;
  });

  // Submit the stored form when clicking confirm
  submitBtn.addEventListener('click', function () {
    var formId = modalEl.dataset.formId;
    var form = formId ? document.getElementById(formId) : null;

    if (!form) {
      // Fallback: just close the modal so the UI isn't stuck
      var bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
      bsModal.hide();
      return;
    }

    submitBtn.disabled = true; // prevent double clicks
    try {
      form.submit(); // navigate to the POST response
    } catch (e) {
      submitBtn.disabled = false;
    }
  });

  // Clean up after hide (optional)
  modalEl.addEventListener('hidden.bs.modal', function () {
    delete modalEl.dataset.formId;
    if (msgEl) msgEl.textContent = 'Are you sure?';
    submitBtn.disabled = false;
  });
});
