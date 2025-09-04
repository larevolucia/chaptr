// --- Rating: single debounced submit on change, with submit lock ---
(function () {
  const DEBOUNCE_MS = 1000;
  const timers = new WeakMap();          // form => timeout id
  const submitting = new WeakMap();      // form => boolean

  function requestSubmit(form) {
    if (!form) return;
    // guard: avoid double-submit even if something else fires
    if (submitting.get(form)) return;
    submitting.set(form, true);

    if (form.requestSubmit) form.requestSubmit();
    else form.submit();
  }

  function debounceSubmit(form) {
    if (!form || submitting.get(form)) return;
    clearTimeout(timers.get(form));
    timers.set(form, setTimeout(() => requestSubmit(form), DEBOUNCE_MS));
  }

  // Single source of truth: any rating change → debounce submit
  document.addEventListener("change", (e) => {
    const radio = e.target.closest('input[name="rating"]');
    if (!radio) return;
    debounceSubmit(radio.form);
  });

  // If something else submits the form, cancel pending timers
  document.addEventListener(
    "submit",
    (e) => {
      const form = e.target.closest("form");
      if (!form) return;
      clearTimeout(timers.get(form));
      submitting.set(form, true);
    },
    true // capture so we see it even if form stops propagation
  );
})();
function removeRating(bookId) {
  const form = document.getElementById(`rating-form-${bookId}`);
  if (form) {
    form.querySelectorAll('input[name="rating"]').forEach(r => (r.checked = false));
    const removeInput = document.createElement("input");
    removeInput.type = "hidden";
    removeInput.name = "rating";
    removeInput.value = "0";
    form.appendChild(removeInput);
    (form.requestSubmit ? form.requestSubmit() : form.submit());
  }
}