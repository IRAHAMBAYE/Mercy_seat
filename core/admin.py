from django.contrib import admin
# 🚨 ACCENT IMPORT HOOK: Updated to include newly launched models to kill any missing compilation NameErrors!
from .models import Sermon, ChurchEvent, PrayerRequest, ChurchImage, ChurchGalleryAsset, MpesaTransaction, ChurchProject

# =====================================================
# 📸 1. SERMONS CATALOGUE MANAGEMENT BOARD
# =====================================================
@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ('title', 'preacher', 'service_type', 'date_preached')
    list_filter = ('service_type', 'date_preached', 'preacher')
    search_fields = ('title', 'preacher', 'summary')
    ordering = ('-date_preached',)
    fieldsets = (
        ('Message Identity', {
            'fields': ('title', 'preacher', 'service_type', 'date_preached')
        }),
        ('Content & Multimedia Logs', {
            'fields': ('summary', 'youtube_url', 'audio_file'),
            'description': 'Input sermon summary scriptures and media streaming url tokens cleanly.'
        }),
    )


# =====================================================
# 📅 2. CHURCH EVENTS & CONFERENCES PROGRAM DESK
# =====================================================
@admin.register(ChurchEvent)
class ChurchEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'location')
    list_filter = ('date', 'location')
    search_fields = ('title', 'description', 'location')
    ordering = ('date', 'start_time')


# =====================================================
# 🙏 3. PASTORAL PRAYER DESK INTERCESSION BOX
# =====================================================
@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'sender_phone', 'date_submitted', 'is_reviewed_by_pastor')
    list_filter = ('is_reviewed_by_pastor', 'date_submitted')
    search_fields = ('sender_name', 'sender_phone', 'prayer_items')
    ordering = ('-date_submitted',)
    list_editable = ('is_reviewed_by_pastor',)
    readonly_fields = ('date_submitted',)


# =====================================================
# 🖼️ 4. CHURCH MEDIA GALLERY ASSETS DESK
# =====================================================
@admin.register(ChurchImage)
class ChurchImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_uploaded')
    search_fields = ('title',)
    ordering = ('-date_uploaded',)


@admin.register(ChurchGalleryAsset)
class ChurchGalleryAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    search_fields = ('title',)
    ordering = ('-uploaded_at',)


# =====================================================
# 💸 5. ONLINE M-PESA REVENUE & AUDITING REPOSITORY
# =====================================================
@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    # Displays clear reference data directly across columns for instant auditing
    list_display = ('mpesa_receipt', 'first_name', 'phone_number', 'transaction_type', 'amount', 'account_reference', 'status', 'created_at')
    # Filters transactions instantly by success type or transaction method
    list_filter = ('transaction_type', 'status', 'created_at', 'account_reference')
    # Search instantly by receipt strings, names, or reference tags
    search_fields = ('mpesa_receipt', 'merchant_request_id', 'checkout_request_id', 'phone_number', 'first_name', 'account_reference')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


# =====================================================
# ⛪ 6. CATHEDRAL VISION PROJECTS MANAGEMENT BOARD
# =====================================================
@admin.register(ChurchProject)
class ChurchProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    # Allows pastors to toggle active status checkboxes straight from the grid row items lists
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('title',)}
