"""Form for book reviews"""
from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for submitting a book review."""
    class Meta:
        """Meta information for the form."""
        model = Review
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Write your thoughts about this book...",
                    "class": "form-control"
                }
            ),
        }
        labels = {
            "content": "Your Review",
        }

    def __init__(self, *args, user, book, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None or book is None:
            raise ValueError("ReviewForm requires both user and book.")
        self.user = user
        self.book = book

    def save(self, commit=True):
        """Attach user and book before saving."""
        review = super().save(commit=False)
        if self.user:
            review.user = self.user
        if self.book:
            review.book = self.book
        if commit:
            review.save()
        return review
