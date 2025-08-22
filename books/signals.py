from django.db.models.signals import post_save
from django.dispatch import receiver

from activity.models import Rating, ReadingStatus, Review


@receiver(post_save, sender=Rating)
def ensure_read_status_on_rating(sender, instance: Rating, created: bool, **kwargs):
    """
    If a user rates a book that currently has no status,
    create a new ReadingStatus with status=READ.
    """
    user = instance.user
    book = instance.book
    # Only act when there is no status yet
    if not ReadingStatus.objects.filter(user=user, book=book).exists():
        ReadingStatus.objects.create(
            user=user,
            book=book,
            status=ReadingStatus.Status.READ
        )


@receiver(post_save, sender=Review)
def ensure_read_status_on_review(sender, instance: Review, created: bool, **kwargs):
    """
    If a user posts/updates a review and has no reading status yet,
    create a new ReadingStatus with status=READ.
    """
    user = instance.user
    book = instance.book
    if not ReadingStatus.objects.filter(user=user, book=book).exists():
        ReadingStatus.objects.create(
            user=user,
            book=book,
            status=ReadingStatus.Status.READ
        )