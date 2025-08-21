document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll("form[id^='rating-form-']").forEach(form => {
    form.querySelectorAll("input[name='rating']").forEach(radio => {
      radio.addEventListener("change", function() {
        form.submit();
      });
    });
  });
});
