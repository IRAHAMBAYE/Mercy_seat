from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
# 📸 4. SANCTUARY MEDIA GALLERY IMAGES
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


# =====================================================
# 💸 5. ONLINE M-PESA FINANCIAL TRANSACTION LEDGER
# =====================================================
class MpesaTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('STK_PUSH', 'Lipa Na M-Pesa Online (STK)'),
        ('C2B', 'Paybill Manual SIM Toolkit Entry'),
        ('B2C', 'Pastoral Welfare / Disbursement Outward'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Implementation'),
        ('COMPLETED', 'Completed Glory Payment'),
        ('FAILED', 'Failed / Cancelled / Insufficient'),
    ]

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    mpesa_receipt = models.CharField(max_length=50, unique=True, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    account_reference = models.CharField(max_length=100, help_text="e.g., Tithe, Building Fund, Welfare Remarks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    first_name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} — KSH {self.amount} ({self.status})"


# =====================================================
# ⛪ 6. CHURCH VISION PROJECTS & TARGETED FUNDING
# =====================================================
class ChurchProject(models.Model):
    title = models.CharField(max_length=255, help_text="e.g., Sanctuary Roofing Extension Phase 2")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Auto-generated url identifier token.")
    description = models.TextField(help_text="Detailed description of the vision and why the cathedral needs it.")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total budget goal in KES.")
    cover_image = models.ImageField(upload_to='projects/covers/', help_text="Upload high-res architecture design or site snapshot.")
    is_active = models.BooleanField(default=True, help_text="Uncheck to archive completed or paused projects.")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (Goal: KES {self.target_amount})"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def total_raised(self):
        """
        Dynamically calculates all successful M-Pesa seeds contributed
        towards this specific project reference from your transaction history ledger.
        """
        from django.db.models import Sum
        # Matches against account_reference using the project's unique system title
        aggregate = MpesaTransaction.objects.filter(
            account_reference=self.title,
            status='COMPLETED'
        ).aggregate(total=Sum('amount'))
        return aggregate['total'] or 0.00

    @property
    def progress_percentage(self):
        """Calculates visual percentage caps for fluid UI bar scales."""
        if self.target_amount <= 0:
            return 0
        percentage = (float(self.total_raised) / float(self.target_amount)) * 100
        return min(round(percentage, 1), 100.0) # Caps visually at 100%


