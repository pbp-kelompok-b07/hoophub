from django.forms import ModelForm
from review.models import Review

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']
        # widgets = {
        #     'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'type': 'number'}),
        #     'review': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your review here...'}),
        # }