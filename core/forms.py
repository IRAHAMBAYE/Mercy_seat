from django import forms
from .models import Sermon, ChurchEvent, PrayerRequest, ChurchImage, ChurchGalleryAsset

COMMON_INPUT_STYLE = 'width: 100%; padding: 0.75rem; margin-top: 0.5rem; margin-bottom: 1.25rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem;'
COMMON_TEXTAREA_STYLE = 'width: 100%; padding: 0.75rem; margin-top: 0.5rem; margin-bottom: 1.25rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; min-height: 100px; resize: vertical;'
COMMON_FILE_STYLE = 'width: 100%; padding: 0.5rem; margin-top: 0.5rem; margin-bottom: 1.5rem;'

class SermonForm(forms.ModelForm):
    class Meta:
        model = Sermon
        fields = ['title', 'preacher', 'service_type', 'date_preached', 'summary', 'youtube_url', 'audio_file']
        widgets = {
            'title': forms.TextInput(attrs={'style': COMMON_INPUT_STYLE, 'placeholder': 'Enter sermon title'}),
            'preacher': forms.TextInput(attrs={'style': COMMON_INPUT_STYLE}),
            'service_type': forms.Select(attrs={'style': COMMON_INPUT_STYLE}),
            'date_preached': forms.DateInput(attrs={'style': COMMON_INPUT_STYLE, 'type': 'date'}),
            'summary': forms.Textarea(attrs={'style': COMMON_TEXTAREA_STYLE, 'placeholder': 'Key points and scripture anchors...'}),
            'youtube_url': forms.URLInput(attrs={'style': COMMON_INPUT_STYLE, 'placeholder': 'https://youtube.com...'}),
            'audio_file': forms.FileInput(attrs={'style': COMMON_FILE_STYLE, 'accept': 'audio/mp3,audio/*'}),
        }

class ChurchEventForm(forms.ModelForm):
    class Meta:
        model = ChurchEvent
        fields = ['title', 'date', 'start_time', 'location', 'banner_image', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'style': COMMON_INPUT_STYLE, 'placeholder': 'Event title'}),
            'date': forms.DateInput(attrs={'style': COMMON_INPUT_STYLE, 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'style': COMMON_INPUT_STYLE, 'type': 'time'}),
            'location': forms.TextInput(attrs={'style': COMMON_INPUT_STYLE}),
            'banner_image': forms.FileInput(attrs={'style': COMMON_FILE_STYLE, 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'style': COMMON_TEXTAREA_STYLE, 'placeholder': 'Describe the event details...'}),
        }

class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['sender_name', 'sender_phone', 'prayer_items']
        widgets = {
            'sender_name': forms.TextInput(attrs={'style': COMMON_INPUT_STYLE, 'placeholder': 'Your Name (Leave blank for Anonymous)'}),
            'sender_phone': forms.TextInput(attrs={'style': COMMON_INPUT_STYLE, 'placeholder': 'Phone Number (Optional)'}),
            'prayer_items': forms.Textarea(attrs={'style': COMMON_TEXTAREA_STYLE, 'placeholder': 'Write your prayer requests here...'}),
        }

class ChurchImageForm(forms.ModelForm):
    class Meta:
        model = ChurchImage
        fields = ['title', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'style': COMMON_INPUT_STYLE, 'placeholder': 'e.g. Sunday Main Praise Team Worship'}),
            'image': forms.FileInput(attrs={'style': COMMON_FILE_STYLE, 'accept': 'image/*'})
        }

class ChurchGalleryAssetForm(forms.ModelForm):
    class Meta:
        model = ChurchGalleryAsset
        fields = ['title', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'style': COMMON_INPUT_STYLE, 'placeholder': 'e.g. Sunday Main Worship Sliding Banner'}),
            'image': forms.FileInput(attrs={'style': COMMON_FILE_STYLE, 'accept': 'image/*'})
        }


from django import forms
from core.models import ChurchProject

class ChurchProjectForm(forms.ModelForm):
    class Meta:
        model = ChurchProject
        fields = ['title', 'description', 'target_amount', 'cover_image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Select Spreadsheet File (.csv)",
        help_text="Upload an official church transaction backup sheet to process rows."
    )
