document.addEventListener('DOMContentLoaded', function () {
    var modalEl = document.getElementById('confirmDeleteModal');
    if (!modalEl) return;

    modalEl.addEventListener('show.bs.modal', function (event) {
      var trigger = event.relatedTarget; // the button that opened the modal
      var action = trigger?.getAttribute('data-action');
      var form = modalEl.querySelector('#deleteReviewForm');
      if (action && form) form.setAttribute('action', action);
    });
});
