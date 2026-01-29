from django.db import models
#from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

isbn_validator = RegexValidator(
    regex=r'^(?:\d{10}|\d{13})$',
    message="ISBN must be 10 or 13 digits (no hyphens allowed here)",
    code='invalid_isbn'
)

class Book(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    author = models.CharField(max_length=255, blank=False, null=False)
    isbn = models.CharField(
        max_length=20,
        unique=True,
        blank=False,
        null=False,
        validators=[isbn_validator],
        help_text='ISBN-10 or ISBN-13 without hyphens'
        )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"{self.title} by {self.author}"
        
    @property
    def is_available(self) -> bool:
        """Derived: True if no active loan exists for this book."""
        return not self.loans.filter(returned_at__isnull=True).exists()
    
    @property
    def current_loan(self):
        """Returns the active loan if any, else None."""
        return self.loans.filter(returned_at__isnull=True).first()
    
class Loan(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name='loans',
        help_text='The book being borrowed'
    )    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='loans',
        help_text='The borrowing user'
    )
    borrowed_at = models.DateTimeField(default=timezone.now, editable=False)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ['-borrowed_at']
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
        # Partial unique index: only one active loan per book
        constraints = [
            models.UniqueConstraint(
                fields = ['book'],
                condition=models.Q(returned_at__isnull=True),
                name='unique_active_loan_per_book'
            )
        ]

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title} on {self.borrowed_at.date()}"

    def clean(self):
        """ Additional model-level validation. """
        if self.due_date <= self.borrowed_at:
            raise ValidationError("Due date must be after borrow date.")
        
    def save(self, *args, **kwargs):
        """ Auto validate on save """
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return self.returned_at is None
    
    @property
    def is_overdue(self) -> bool:
        if not self.is_active:
            return False
        return timezone.now() > self.due_date

        

