from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from activity.models import ReadingStatus


# Create your views here.
@login_required
def library_list(request):
    """Display the user's library with reading statuses."""
    rows = (
        ReadingStatus.objects
        .filter(user=request.user)
        .select_related("book")
        .order_by("-updated_at")
    )

    labels = dict(ReadingStatus.Status.choices)
    status_class = {
        ReadingStatus.Status.TO_READ: "status--to-read",
        ReadingStatus.Status.READING: "status--reading",
        ReadingStatus.Status.READ: "status--read",
    }
    for rs in rows:
        rs.user_status_label = labels.get(rs.status, "—")
        rs.user_status_class = status_class.get(rs.status, "status--none")

    return render(request, "library/library_list.html", {"rows": rows})
