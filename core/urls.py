# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ⛪ SANCTUARY ROOT LANDING HOME GATEWAY
    path('', views.church_home, name='church_home'),

    # 💸 ONLINE M-PESA KINGDOM SEED TITHES & OFFERINGS PORTALS
    path('give/', views.church_giving_portal, name='church_giving_portal'),

    # 📸 SERMONS MEDIA CENTER GALLERY MATRIX
    path('sermons/', views.sermons_center, name='sermons_center'),

    # 🙏 DIGITAL PRAYER REQUEST REPOSITORY BOX DESK
    path('prayer-desk/', views.prayer_desk, name='prayer_desk'),

    # 📅 UPCOMING CHURCH EVENTS & CONFERENCES CALENDAR
    path('events/', views.events_log, name='events_log'),

    # ⛪ PASTOR'S PRIVATE LEADERSHIP PANEL & ACTION CHANNELS
    path('pastoral/dashboard/', views.pastor_dashboard, name='pastor_dashboard'),

    # 🔒 NEW: PASTOR ADMINISTRATIVE CONTROL DESK (FOR UPLOADS AND CATALOG MANAGEMENT)
    path('pastoral/admin-desk/', views.pastor_admin_desk, name='pastor_admin_desk'),

    # ⚡ OPERATIONAL TRIGGER ENGINES
    path('pastoral/prayer/clear/<int:prayer_id>/', views.mark_prayer_reviewed, name='mark_prayer_reviewed'),
    path('pastoral/media/delete/<int:asset_id>/<str:asset_type>/', views.delete_gallery_asset,
         name='delete_gallery_asset'),

    path('pastoral/admin-desk/', views.pastor_admin_desk, name='pastor_admin_desk'),

]
