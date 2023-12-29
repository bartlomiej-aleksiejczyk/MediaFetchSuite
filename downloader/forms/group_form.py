from django import forms

from mediafetchxpress.link_type_choices import LINK_TYPE_CHOICES
from mediafetchxpress.models import Group


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'link_type']
        widgets = {
            'link_type': forms.Select(choices=LINK_TYPE_CHOICES)
        }