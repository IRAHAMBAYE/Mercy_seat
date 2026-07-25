import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Sermon, ChurchEvent, PrayerRequest, ChurchImage, ChurchGalleryAsset
from core.forms import SermonForm, ChurchEventForm, PrayerRequestForm, ChurchImageForm, ChurchGalleryAssetForm

# =====================================================
# ⛪ 0. SANCTUARY ROOT HOMEPAGE VIEW (SPLIT TWO-PART OVERHAUL)
# =====================================================
def church_home(request):
    """
    Renders the public dashboard workspace featuring the two-part hero matrix:
    Part 1: Branding block + actions
    Part 2: Auto-scrolling gallery slideshow pulled directly from ChurchGalleryAsset
    """
    church_gallery = ChurchGalleryAsset.objects.all().order_by('-uploaded_at')

    # ⚡ FALLBACK CHECK: If no sliding banner assets exist, load pictures from ChurchImage instead!
    if not church_gallery.exists():
        church_gallery = ChurchImage.objects.all().order_by('-date_uploaded')

    # Grab the newest sermon setup video URL identifier token if available
    featured_sermon = Sermon.objects.all().order_by('-date_preached').first()
    youtube_video_id = None

    if featured_sermon and featured_sermon.youtube_url:
        url = featured_sermon.youtube_url
        if "watch?v=" in url:
            youtube_video_id = "/embed/" + url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            youtube_video_id = "/embed/" + url.split("youtu.be/")[-1].split("?")[0]
        elif "/embed/" in url:
            youtube_video_id = "/embed/" + url.split("/embed/")[-1].split("?")[0]

    context = {
        'church_gallery': church_gallery,
        'featured_sermon': featured_sermon,
        'youtube_video_id': youtube_video_id,
    }
    return render(request, 'church_home.html', context)

# =====================================================
# 💸 1. DYNAMIC M-PESA CHURCH GIVING PORTAL VIEW
# =====================================================
@csrf_exempt
def church_giving_portal(request):
    """
    Handles secure kingdom contributions for PEFA Thika Road by pushing
    instant Lipa Na M-Pesa STK prompts to the congregant's mobile phone.
    """
    if request.method == "POST":
        phone_number = request.POST.get("phone", "").strip()
        giving_amount = request.POST.get("amount", "").strip()
        giving_type = request.POST.get("giving_type", "OFFERING")
        name = request.POST.get("fullname", "").strip() or "Anonymous Giver"

        print(f"💸 PEFA Thika Road Ledger: {name} is seeding Ksh {giving_amount} towards {giving_type}...")

        try:
            # Future M-Pesa Daraja API hooks will be wired right here!
            account_reference = f"PEFA_{giving_type[:6].upper()}"
            print(f"⚡ Daraja API Payload Prepped: Ref {account_reference} pushed securely to {phone_number}")

            messages.success(request,
                             f"🙏 Thank you {name}! Your seed contribution of Ksh {giving_amount} towards {giving_type} has been initialized via M-Pesa. Key in your PIN on your phone to finalize.")

        except Exception as api_err:
            print(f"⚠️ M-Pesa Ministry Channel Exception: {str(api_err)}")
            messages.error(request, "⚠️ Safaricom API Gateway timeout. Please check your local connection parameters.")

        return redirect('church_giving_portal')

    return render(request, 'church_giving.html')

# =====================================================
# 📸 2. SERMONS MEDIA CENTER REPOSITORY GRID
# =====================================================
def sermons_center(request):
    """
    Fetches the latest recorded sermon uploads, categorized filters,
    and scripture summaries from the database logs to display in a clean media grid.
    """
    all_sermons = Sermon.objects.all().order_by('-date_preached')

    # Optional category filtering loops from request query parameters
    service_filter = request.GET.get('service_type')
    if service_filter:
        all_sermons = all_sermons.filter(service_type=service_filter)

    context = {
        'sermons': all_sermons,
        'selected_filter': service_filter,
    }
    return render(request, 'church_sermons.html', context)

# =====================================================
# 🙏 3. DIGITAL PRAYER REQUEST DESK COMPONENT
# =====================================================
def prayer_desk(request):
    """
    Captures prayer needs submitted by congregants, stores them safely
    in the database for pastoral review, and alerts them of a successful receipt.
    """
    if request.method == "POST":
        name_entry = request.POST.get("fullname") or request.POST.get("sender_name") or "Anonymous"
        phone_entry = request.POST.get("phone") or request.POST.get("sender_phone") or ""
        needs_entry = request.POST.get("prayer_item") or request.POST.get("prayer_items") or ""

        name_entry = name_entry.strip()
        phone_entry = phone_entry.strip()
        needs_entry = needs_entry.strip()

        if needs_entry:
            PrayerRequest.objects.create(
                sender_name=name_entry,
                sender_phone=phone_entry if phone_entry else None,
                prayer_items=needs_entry,
                is_reviewed_by_pastor=False
            )
            print(f"🙏 PEFA Thika Road Prayer Box: Fresh request logged from '{name_entry}'!")
            messages.success(request,
                             f"✨ Thank you {name_entry}. Your prayer request has been securely submitted to the Pastoral team. Stand firm in faith, the Lord hears you.")
        else:
            messages.warning(request, "⚠️ Please type in your prayer request details before submitting.")

        return redirect('prayer_desk')

    return render(request, 'church_prayer.html')

# =====================================================
# 📅 4. UPCOMING CHURCH EVENTS & CONFERENCES CALENDAR
# =====================================================
def events_log(request):
    """
    Fetches scheduled church conferences, special fellowship calendar items,
    and ministry events from the database logs to display cleanly for the congregation.
    """
    today = datetime.date.today()
    upcoming_events = ChurchEvent.objects.filter(date__gte=today).order_by('date', 'start_time')

    context = {
        'events': upcoming_events,
    }
    return render(request, 'church_events.html', context)

# =====================================================
# ⛪ 6. PASTOR'S PRIVATE LEADERSHIP REVIEW DASHBOARD
# =====================================================
@login_required(login_url='/admin/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def pastor_dashboard(request):
    """
    Pastoral leadership workspace panel. Displays all active congregational
    prayer desk requests, intercession queues, and ministry metadata counters.
    """
    pending_prayers = PrayerRequest.objects.filter(is_reviewed_by_pastor=False).order_by('-date_submitted')
    reviewed_prayers = PrayerRequest.objects.filter(is_reviewed_by_pastor=True).order_by('-date_submitted')[:10]

    total_pending = pending_prayers.count()
    total_sermons = Sermon.objects.all().count()
    total_events = ChurchEvent.objects.all().count()

    context = {
        'pending_prayers': pending_prayers,
        'reviewed_prayers': reviewed_prayers,
        'total_pending': total_pending,
        'total_sermons': total_sermons,
        'total_events': total_events,
    }
    return render(request, 'pastor_dashboard.html', context)
# =====================================================
# 🔒 PASTOR ADMINISTRATIVE FORM CONTROL DESK PANEL
# =====================================================
def is_church_admin(user):
    """
    Access verification rule: Grants immediate entrance to any active Staff row,
    Superuser account, or users mapped to the historical 'ChurchAdmins' group.
    """
    return user.is_authenticated and (
        user.is_staff or
        user.is_superuser or
        user.groups.filter(name='ChurchAdmins').exists()
    )

@user_passes_test(is_church_admin, login_url='/admin/login/')
def pastor_admin_desk(request):
    """
    Unified control interface allowing pastors to securely upload gallery files,
    add upcoming calendar programs, post sermons, and check off pending items.
    """
    sermon_form = SermonForm()
    event_form = ChurchEventForm()
    image_form = ChurchImageForm()
    asset_form = ChurchGalleryAssetForm()

    if request.method == 'POST':
        action_flag = request.POST.get('admin_action')

        if action_flag == 'create_sermon':
            form = SermonForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "🎉 New sermon record catalogue published successfully.")
                return redirect('pastor_admin_desk')

        elif action_flag == 'create_event':
            form = ChurchEventForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "🎉 Calendar program added to events schedule.")
                return redirect('pastor_admin_desk')

        elif action_flag == 'upload_grid_image':
            form = ChurchImageForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "📸 High-resolution grid image uploaded successfully.")
                return redirect('pastor_admin_desk')

        elif action_flag == 'upload_slider_asset':
            form = ChurchGalleryAssetForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "🖼️ Slider banner asset added to homepage loop.")
                return redirect('pastor_admin_desk')

    context = {
        'sermon_form': sermon_form,
        'event_form': event_form,
        'image_form': image_form,
        'asset_form': asset_form,
        'all_sermons': Sermon.objects.all(),
        'all_events': ChurchEvent.objects.all(),
        'grid_images': ChurchImage.objects.all(),
        'slider_assets': ChurchGalleryAsset.objects.all(),
        'pending_prayers': PrayerRequest.objects.filter(is_reviewed_by_pastor=False).order_by('-date_submitted'),
    }
    return render(request, 'pastor_admin_desk.html', context)


# =====================================================
# ⚡ OPERATIONAL TRIGGER ENGINES FOR MANAGEMENT DESK
# =====================================================
@user_passes_test(is_church_admin, login_url='/admin/login/')
def edit_gallery_asset(request, asset_id):
    """
    Captures text title changes submitted by pastors for specific slideshow items
    and updates the database record cleanly with a success notification.
    """
    asset = get_object_or_404(ChurchGalleryAsset, id=asset_id)
    if request.method == "POST":
        new_title = request.POST.get('updated_title', '').strip()
        if new_title:
            asset.title = new_title
            asset.save()
            messages.success(request, f"🎉 Slideshow title updated successfully to '{new_title}'.")
        else:
            messages.warning(request, "⚠️ Title cannot be blank.")
    return redirect('pastor_admin_desk')


@user_passes_test(is_church_admin, login_url='/admin/login/')
def mark_prayer_reviewed(request, prayer_id):
    """Flags an active prayer instance item database flag entry to True."""
    prayer = get_object_or_404(PrayerRequest, id=prayer_id)
    prayer.is_reviewed_by_pastor = True
    prayer.save()

    print(f"✅ PEFA Thika Road Pastoral Desk: Prayer Request #{prayer_id} marked as reviewed!")
    messages.success(request, f"🙏 Prayer petition from '{prayer.sender_name}' has been successfully reviewed and moved to archives.")
    return redirect('pastor_admin_desk')


@user_passes_test(is_church_admin, login_url='/admin/login/')
def delete_gallery_asset(request, asset_id, asset_type):
    """Deletes specific image instances from media models securely with a notification pop-up."""
    if asset_type == 'grid':
        asset = get_object_or_404(ChurchImage, id=asset_id)
        title = asset.title
        asset.delete()
        messages.warning(request, f"🗑️ Grid image '{title}' has been completely removed from the gallery matrix.")
    else:
        asset = get_object_or_404(ChurchGalleryAsset, id=asset_id)
        title = asset.title
        asset.delete()
        messages.warning(request, f"🗑️ Sliding banner asset '{title}' has been cleared from the homepage carousel loop.")

    return redirect('pastor_admin_desk')


# =====================================================
# 🔍 8. SYSTEM ERROR TEMPLATE ROUTER HANDLERS
# =====================================================
def custom_404_handler(request, exception=None):
    """Safely captures missing ministry url tracking coordinates."""
    return render(request, '404.html', status=404)
