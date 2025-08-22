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
            "content": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Write your thoughts about this book...",
                "class": "form-control",
            }),
        }
        labels = {"content": "Your Review"}

    def __init__(self, *args, **kwargs):
        """Initialize the form with user and book context."""
        self.user = kwargs.pop("user", None)
        self.book = kwargs.pop("book", None)
        self.book_id = kwargs.pop("book_id", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        review = super().save(commit=False)
        if self.user is not None:
            review.user = self.user
        if self.book is not None:
            review.book = self.book
        elif self.book_id is not None:
            review.book_id = self.book_id
        if commit:
            review.save()
        return review
