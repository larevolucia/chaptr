from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import render
from activity.models import ReadingStatus


# Create your views here.
@login_required
def library(request):
    """Display the user's library with reading statuses."""
    status_param = (request.GET.get("status", "ALL") or "ALL").upper()
    
    sort = request.GET.get("sort", "updated")   # default sort
    direction = request.GET.get("dir", "desc")  # asc|desc
    prefix = "" if direction == "asc" else "-"

    qs = (
        ReadingStatus.objects
        .filter(user=request.user)
        .select_related("book")
    )

    VALID = {
        "TO_READ": ReadingStatus.Status.TO_READ,
        "READING": ReadingStatus.Status.READING,
        "READ":    ReadingStatus.Status.READ,
    }

    if status_param in VALID:
        qs = qs.filter(status=VALID[status_param])
    if sort == "status":
        status_order = Case(
            When(status=ReadingStatus.Status.TO_READ,  then=Value(0)),
            When(status=ReadingStatus.Status.READING, then=Value(1)),
            When(status=ReadingStatus.Status.READ,    then=Value(2)),
            default=Value(99),
            output_field=IntegerField(),
        )
        qs = qs.annotate(_status_order=status_order)\
               .order_by(f"{prefix}_status_order", f"{prefix}updated_at")
    elif sort == "added":
        qs = qs.order_by(f"{prefix}created_at")
    elif sort == "updated":
        qs = qs.order_by(f"{prefix}updated_at")
    else:
        qs = qs.order_by("-updated_at")  # safe default

    rows = qs

    labels = dict(ReadingStatus.Status.choices)

    status_class = {
        ReadingStatus.Status.TO_READ: "status--to-read",
        ReadingStatus.Status.READING: "status--reading",
        ReadingStatus.Status.READ: "status--read",
    }
    for rs in rows:
        rs.user_status_label = labels.get(rs.status, "—")
        rs.user_status_class = status_class.get(rs.status, "status--none")

    return render(request, "library/library.html", {"rows": rows, "status_param": status_param, "sort": sort, "direction": direction})
