
document.addEventListener("DOMContentLoaded", function() {
  // Handle rating changes
  document.querySelectorAll("form[id^='rating-form-']").forEach(form => {
    form.querySelectorAll("input[name='rating']").forEach(radio => {
      radio.addEventListener("change", function() {
        form.submit();
      });
    });
  });
});

// Function to remove rating
function removeRating(bookId) {
  const form = document.getElementById(`rating-form-${bookId}`);
  if (form) {
    // Clear all radio buttons
    form.querySelectorAll("input[name='rating']").forEach(radio => {
      radio.checked = false;
    });
    
    // Add hidden input to signal removal
    const removeInput = document.createElement("input");
    removeInput.type = "hidden";
    removeInput.name = "rating";
    removeInput.value = "0";
    form.appendChild(removeInput);
    
    form.submit();
  }
}