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

    # 🔒 PASTOR ADMINISTRATIVE CONTROL DESK (FOR UPLOADS AND CATALOG MANAGEMENT)
    path('pastoral/admin-desk/', views.pastor_admin_desk, name='pastor_admin_desk'),

    # ⚡ OPERATIONAL TRIGGER ENGINES
    path('pastoral/prayer/clear/<int:prayer_id>/', views.mark_prayer_reviewed, name='mark_prayer_reviewed'),
    path('pastoral/media/delete/<int:asset_id>/<str:asset_type>/', views.delete_gallery_asset,
         name='delete_gallery_asset'),

    # ✏️ NEW: INLINE SLIDESHOW CAPTION MODIFICATION ROUTE ENDPOINT
    path('pastoral/edit-asset/<int:asset_id>/', views.edit_gallery_asset, name='edit_gallery_asset'),

    path('api/v1/mpesa/stk-callback/', views.mpesa_stk_callback, name='mpesa_stk_callback'),
    path('api/v1/mpesa/c2b-validation/', views.mpesa_c2b_validation, name='mpesa_c2b_validation'),
    path('api/v1/mpesa/c2b-confirmation/', views.mpesa_c2b_confirmation, name='mpesa_c2b_confirmation'),
    # 💸 OUTWARD B2C WELFARE PAYMENT DISBURSEMENT ENGINE
    path('pastoral/disburse-b2c/', views.trigger_pastoral_b2c, name='trigger_pastoral_b2c'),
    # ⛪ CATHEDRAL DEVELOPMENT PROJECTS & PROGRESS MATRIX
    path('projects/', views.projects_directory, name='projects_directory'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    # 📥 EXCEL TRANSACTION LEDGER SHEET EXPORTER PIPELINE
    path('pastoral/dashboard/export-csv/', views.export_financial_ledger_csv, name='export_financial_ledger_csv'),
    # 📥 EXCEL TRANSACTION SPREADSHEET IMPORTER ROUTE
    path('pastoral/dashboard/import-csv/', views.import_financial_ledger_csv, name='import_financial_ledger_csv'),

]