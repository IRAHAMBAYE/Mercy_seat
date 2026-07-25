from django.db import models
from django.contrib.auth.models import User


# =====================================================
# 📑 1. SERMON MEDIA CENTER CATALOGUE RECORD
# =====================================================
class Sermon(models.Model):
    SERMON_TYPE_CHOICES = [
        ('SUNDAY', 'Sunday Main Service'),
        ('MIDWEEK', 'Mid-Week Midweek Service'),
        ('YOUTH', 'Youth Fellowship Explosion'),
        ('CONFERENCE', 'Special Ministry Conference'),
    ]

    title = models.CharField(max_length=255)
    preacher = models.CharField(max_length=150, default="Senior Pastor")
    service_type = models.CharField(max_length=20, choices=SERMON_TYPE_CHOICES, default='SUNDAY')
    date_preached = models.DateField()
    summary = models.TextField(help_text="Brief summary of the sermon keys and scripture anchors.")
    youtube_url = models.URLField(blank=True, null=True, help_text="Paste live streaming or recording link.")
    audio_file = models.FileField(upload_to='sermons/audio/', blank=True, null=True,
                                  help_text="Upload MP3 format for local listening downloads.")

    class Meta:
        ordering = ['-date_preached']

    def __str__(self):
        return f"{self.title} — By {self.preacher} ({self.date_preached})"


# =====================================================
# 📅 2. UPCOMING CHURCH EVENTS & CONFERENCES CALENDAR
# =====================================================
class ChurchEvent(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    location = models.CharField(max_length=255, default="PEFA Thika Road Sanctuary")
    banner_image = models.ImageField(upload_to='events/banners/', blank=True, null=True)
    description = models.TextField()

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} — On {self.date}"


# =====================================================
# 🙏 3. DIGITAL PRAYER REQUEST REPOSITORY DESK
# =====================================================
class PrayerRequest(models.Model):
    sender_name = models.CharField(max_length=150, blank=True, default="Anonymous")
    sender_phone = models.CharField(max_length=20, blank=True, null=True)
    prayer_items = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_reviewed_by_pastor = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_submitted']

    def __str__(self):
        return f"Prayer Box Entry #{self.id} — {self.sender_name} ({self.date_submitted.date()})"


# =====================================================
# 📸 4. SANCTUARY MEDIA GALLERY IMAGES (NEW)
# =====================================================
class ChurchImage(models.Model):
    title = models.CharField(max_length=150, help_text="e.g. Sunday Main Praise Team Worship")
    image = models.ImageField(upload_to='gallery/church/', help_text="Upload high-resolution landscape images.")
    date_uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_uploaded']

    def __str__(self):
        return f"Gallery Asset: {self.title} ({self.date_uploaded.date()})"


class ChurchGalleryAsset(models.Model):
    title = models.CharField(max_length=200,
                             help_text="Enter a caption for the slide activity (e.g., Sunday Main Worship)")
    image = models.ImageField(upload_to='church_gallery/',
                              help_text="Upload landscape-oriented sanctuary lifestyle pictures")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
