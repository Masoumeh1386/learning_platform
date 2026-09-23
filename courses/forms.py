from django import forms
from .models import Course, Lesson,Comment,Rating


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'slug', 'short_description', 'description',
                  'category', 'image', 'price', 'level', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'short_description': forms.TextInput(attrs={'placeholder': 'توضیح کوتاه'}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'نظرت رو بنویس...'}),
        }


class RatingForm(forms.ModelForm):
    SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    score = forms.ChoiceField(choices=SCORE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Rating
        fields = ['score']