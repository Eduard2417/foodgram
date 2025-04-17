from django import forms

from .models import Recipe, Tag


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = '__all__'
