from django.contrib import admin
# 🚨 ACCENT IMPORT HOOK: Added ChurchImage to the list here to kill the NameError crash!
from .models import Sermon, ChurchEvent, PrayerRequest, ChurchImage

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
