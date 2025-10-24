from django.forms import ModelForm
from report.models import Report
from django.utils.html import strip_tags

class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'description']

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        return strip_tags(title)

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        return strip_tags(description)
