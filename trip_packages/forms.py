from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from .models import Reviews
import re


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ['title', 'rating', 'comment', 'image']

    title = forms.CharField(max_length=30, required=True)
    rating = forms.IntegerField(required=True)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        max_length=300,
        required=True
    )

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)

        custom_classes = 'border-black rounded-0 review-form-input'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = custom_classes

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if isinstance(image, UploadedFile):
                if image.size > (5 * 1024 * 1024):
                    raise ValidationError('File size must be no more than 5mb.')
                if image.content_type not in ['image/jpeg', 'image/png']:
                    raise ValidationError('File format must be JPEG or PNG.')
        return image

    def clean_rating(self):
        print("Cleaning rating")
        rating = self.cleaned_data.get('rating')
        if rating not in range(1, 6):
            raise ValidationError('Rating must be between 1 and 5.')
        return rating

    def clean_title(self):
        print("Cleaning title")
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("Title cannot be empty.")
        if re.search('[^a-zA-Z0-9 ]', title):
            raise ValidationError("Title should only contain alphanumeric "
                                  "characters and spaces.")
        return title

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if not comment:
            raise ValidationError("Comment cannot be empty.")
        if len(comment) < 50:
            raise ValidationError("Comment should be at least "
                                  "50 characters long.")
        return comment
