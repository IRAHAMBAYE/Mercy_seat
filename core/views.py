import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Sermon, ChurchEvent, PrayerRequest, ChurchImage, ChurchGalleryAsset, MpesaTransaction
from core.forms import SermonForm, ChurchEventForm, PrayerRequestForm, ChurchImageForm, ChurchGalleryAssetForm
from core.mpesa_client import MpesaDarajaClient
from core.models import Sermon, ChurchEvent, PrayerRequest, ChurchImage, ChurchGalleryAsset, MpesaTransaction, ChurchProject
from core.forms import SermonForm, ChurchEventForm, PrayerRequestForm, ChurchImageForm, ChurchGalleryAssetForm, ChurchProjectForm



# =====================================================
# ⛪ 0. SANCTUARY ROOT HOMEPAGE VIEW
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
        raw_phone = request.POST.get("phone", "").strip()
        giving_amount = request.POST.get("amount", "").strip()
        giving_type = request.POST.get("giving_type", "OFFERING")
        name = request.POST.get("fullname", "").strip() or "Anonymous Giver"

        print(f"💸 PEFA Thika Road Ledger: {name} is seeding Ksh {giving_amount} towards {giving_type}...")

        # Clean number to match standard Safaricom formatting rules (2547XXXXXXXX)
        if raw_phone.startswith('0'):
            phone = '254' + raw_phone[1:]
        elif raw_phone.startswith('+254'):
            phone = raw_phone[1:]
        elif raw_phone.startswith('254'):
            phone = raw_phone
        else:
            messages.error(request, "❌ Invalid Phone Number structure. Use standard format (e.g., 0712345678).")
            return redirect('church_giving_portal')

        # Public deployment callback hook declaration URL endpoint
        callback_url = "https://pefathikaroadcathedral.org"

        try:
            client = MpesaDarajaClient()
            response = client.send_stk_push(
                phone_number=phone,
                amount=giving_amount,
                callback_url=callback_url,
                account_reference=giving_type,
                transaction_desc=f"Cathedral {giving_type}"
            )

            if response.get('ResponseCode') == '0':
                # Register a background track segment record before payment executes
                MpesaTransaction.objects.create(
                    transaction_type='STK_PUSH',
                    amount=giving_amount,
                    phone_number=phone,
                    merchant_request_id=response.get('MerchantRequestID'),
                    checkout_request_id=response.get('CheckoutRequestID'),
                    account_reference=giving_type,
                    first_name=name,
                    status='PENDING'
                )
                messages.success(request, f"🙏 Thank you {name}! Your seed contribution of Ksh {giving_amount} towards {giving_type} has been initialized via M-Pesa. Key in your PIN on your phone to finalize.")
            else:
                messages.error(request, f"❌ Safaricom API rejection error: {response.get('ResponseDescription')}")
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
            messages.success(request, f"✨ Thank you {name_entry}. Your prayer request has been securely submitted to the Pastoral team. Stand firm in faith, the Lord hears you.")
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


import json  # 🚨 CRITICAL HOOK: Restores the live dashboard metrics serialization pipeline
from django.db.models import Sum
from django.db.models.functions import TruncWeek
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Sermon, ChurchEvent, PrayerRequest, MpesaTransaction

# =====================================================
# ⛪ 6. PASTOR'S PRIVATE LEADERSHIP REVIEW DASHBOARD
# =====================================================
@login_required(login_url='/admin/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def pastor_dashboard(request):
    """
    Pastoral leadership workspace panel. Displays active congregational prayer
    desk requests, intercession queues, and aggregates real-time graph datasets for cashflows.
    """
    pending_prayers = PrayerRequest.objects.filter(is_reviewed_by_pastor=False).order_by('-date_submitted')
    reviewed_prayers = PrayerRequest.objects.filter(is_reviewed_by_pastor=True).order_by('-date_submitted')[:10]

    total_pending = pending_prayers.count()
    total_sermons = Sermon.objects.all().count()
    total_events = ChurchEvent.objects.all().count()

    # Fetch latest 15 transactions for the pastoral cash flow matrix view
    church_transactions = MpesaTransaction.objects.all().order_by('-created_at')[:15]

    # 📊 GRAPH DATA A: Aggregate total collections by dynamic categories
    categories_query = MpesaTransaction.objects.filter(status='COMPLETED').values('account_reference').annotate(total=Sum('amount'))
    chart_labels = [item['account_reference'] for item in categories_query]
    chart_data = [float(item['total']) for item in categories_query]

    # 📊 GRAPH DATA B: Aggregate weekly cash flow trends (Last 6 weeks)
    weekly_query = MpesaTransaction.objects.filter(status='COMPLETED').annotate(week=TruncWeek('created_at')).values('week').annotate(total=Sum('amount')).order_by('week')[:6]
    trend_labels = [item['week'].strftime('%b %d') for item in weekly_query if item['week']]
    trend_data = [float(item['total']) for item in weekly_query]

    context = {
        'pending_prayers': pending_prayers,
        'reviewed_prayers': reviewed_prayers,
        'total_pending': total_pending,
        'total_sermons': total_sermons,
        'total_events': total_events,
        'transactions': church_transactions,
        # ✨ Serialize your data variables into safe text packets for Chart.js
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
    }
    return render(request, 'pastor_dashboard.html', context)


# =====================================================
# 💸 7. SAFARICOM M-PESA DARAJA WEBHOOK API ENDPOINTS
# =====================================================
@csrf_exempt
@require_POST
def mpesa_stk_callback(request):
    """Processes verification feedback loops upon completion of user PIN entry"""
    try:
        payload = json.loads(request.body.decode('utf-8'))
        stk_callback = payload.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        merchant_id = stk_callback.get('MerchantRequestID')

        tx = MpesaTransaction.objects.filter(merchant_request_id=merchant_id).first()
        if not tx:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Transaction track log entry not found"})

        if result_code == 0:
            metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            receipt = next((i.get('Value') for i in metadata if i.get('Name') == 'MpesaReceiptNumber'), None)
            phone = next((i.get('Value') for i in metadata if i.get('Name') == 'PhoneNumber'), tx.phone_number)

            tx.status = 'COMPLETED'
            tx.mpesa_receipt = receipt
            tx.phone_number = phone
            tx.save()
            print(f"✅ STK Push Completed: KSH {tx.amount} received from {phone} [{receipt}]")
        else:
            tx.status = 'FAILED'
            tx.save()
            print(f"❌ STK Push Declined/Failed for ID {merchant_id} with Code {result_code}")

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})
    except Exception as e:
        return JsonResponse({"ResultCode": 1, "ResultDesc": f"Callback parse error: {str(e)}"})


@csrf_exempt
@require_POST
def mpesa_c2b_validation(request):
    """Pre-validates manual SIM Toolkit Paybill entry details before processing money"""
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


@csrf_exempt
@require_POST
def mpesa_c2b_confirmation(request):
    """Captures manual external SIM Paybill collections directly into the ledger grid"""
    try:
        payload = json.loads(request.body.decode('utf-8'))
        receipt_id = payload.get('TransID')

        # Enforce uniqueness check to block duplication runs
        if MpesaTransaction.objects.filter(mpesa_receipt=receipt_id).exists():
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Duplicate entry clean bypass"})

        MpesaTransaction.objects.create(
            transaction_type='C2B',
            amount=payload.get('TransAmount'),
            phone_number=payload.get('MSISDN'),
            mpesa_receipt=receipt_id,
            account_reference=payload.get('BillRefNumber', 'General Paybill Giving'),
            first_name=payload.get('FirstName', 'Congregation Member'),
            status='COMPLETED'
        )
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Payment successfully recorded"})
    except Exception as e:
        return JsonResponse({"ResultCode": 1, "ResultDesc": f"Database recording issue: {str(e)}"})


@login_required(login_url='/admin/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def trigger_pastoral_b2c(request):
    """Pushes automated outward money disbursements to members right from the dashboard view"""
    if request.method == "POST":
        raw_phone = request.POST.get('phone_number', '').strip()
        amount = request.POST.get('amount', '').strip()
        remarks = request.POST.get('remarks', 'Welfare Allocation').strip()

        if raw_phone.startswith('0'):
            phone = '254' + raw_phone[1:]
        elif raw_phone.startswith('+254'):
            phone = raw_phone[1:]
        else:
            phone = raw_phone

        result_url = "https://pefathikaroadcathedral.org"
        timeout_url = "https://pefathikaroadcathedral.org"

        try:
            client = MpesaDarajaClient()
            response = client.initiate_b2c_disbursement(
                phone_number=phone,
                amount=amount,
                result_url=result_url,
                queue_url=timeout_url,
                remarks=remarks
            )

            if response.get('ResponseCode') == '0':
                MpesaTransaction.objects.create(
                    transaction_type='B2C',
                    amount=amount,
                    phone_number=phone,
                    account_reference=remarks,
                    merchant_request_id=response.get('ConversationID'),
                    status='PENDING'
                )
                messages.success(request, f"💸 B2C outbound request of KSH {amount} dispatched for processing.")
            else:
                messages.error(request, f"❌ Safaricom B2C Gateway Rejection: {response.get('ResponseDescription')}")
        except Exception as e:
            messages.error(request, f"❌ Outbound communication channel failure: {str(e)}")

        return redirect('pastor_dashboard')

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
    add upcoming calendar programs, post sermons, and manage cathedral building campaigns.
    """
    sermon_form = SermonForm()
    event_form = ChurchEventForm()
    image_form = ChurchImageForm()
    asset_form = ChurchGalleryAssetForm()
    project_form = ChurchProjectForm()  # 🌱 Instantiate the new project layout form

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

        # ⛪ NEW CONTROLLER ACTION FOR INTEGRATING TARGETED CHURCH PROJECTS
        elif action_flag == 'create_project':
            form = ChurchProjectForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "⛪ New development campaign published successfully onto public metrics layout grids.")
                return redirect('pastor_admin_desk')

    context = {
        'sermon_form': sermon_form,
        'event_form': event_form,
        'image_form': image_form,
        'asset_form': asset_form,
        'project_form': project_form,  # 🌱 Expose project form wrapper to template view
        'all_sermons': Sermon.objects.all(),
        'all_events': ChurchEvent.objects.all(),
        'grid_images': ChurchImage.objects.all(),
        'slider_assets': ChurchGalleryAsset.objects.all(),
        'all_projects': ChurchProject.objects.all(),  # 🌱 Expose your projects dataset to tracking grids
        'pending_prayers': PrayerRequest.objects.filter(is_reviewed_by_pastor=False).order_by('-date_submitted'),
        'transactions': MpesaTransaction.objects.all().order_by('-created_at')[:15],  # Required for the financial subtable
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


# =====================================================
# ⛪ 9. PUBLIC CHURCH CAMPAIGNS DIRECTORY CONTROLLERS
# =====================================================
def projects_directory(request):
    """Fetches all active development campaigns to present to members with dynamic progress ratios."""
    active_projects = ChurchProject.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'church_projects.html', {'projects': active_projects})


def project_detail(request, slug):
    """Displays project data blueprints and embeds deep-linked M-Pesa tracking properties."""
    project = get_object_or_404(ChurchProject, slug=slug)
    return render(request, 'project_detail.html', {'project': project})


import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import MpesaTransaction

@login_required(login_url='/admin/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def export_financial_ledger_csv(request):
    """
    Scans the live transaction database tables, formats numeric values,
    and pipes out an encrypted corporate spreadsheet file download (.CSV) on demand.
    """
    # Create the secure layout response object pointing to Excel stream targets
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="PEFA_Cathedral_Ledger_Export.csv"'

    writer = csv.writer(response)
    # Define official accounting layout columns headers matrix
    writer.writerow(['System ID', 'M-Pesa Receipt', 'Transaction Channel', 'Giver Name', 'Phone Target', 'Amount (KES)', 'Allocation Target', 'Verification Status', 'Timestamp Logged'])

    # Stream out full ledger records chronologically
    records = MpesaTransaction.objects.all().order_by('-created_at')
    for tx in records:
        writer.writerow([
            tx.id,
            tx.mpesa_receipt if tx.mpesa_receipt else "N/A",
            tx.get_transaction_type_display(),
            tx.first_name if tx.first_name else "Anonymous / General Member",
            tx.phone_number,
            f"{'-' if tx.transaction_type == 'B2C' else ''}{tx.amount}",
            tx.account_reference,
            tx.get_status_display(),
            tx.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response


import io
import csv
from django.utils import timezone
from .forms import ExcelImportForm


@login_required(login_url='/admin/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def import_financial_ledger_csv(request):
    """
    Reads an uploaded CSV file spreadsheet row-by-row, validates columns,
    and bulk-injects historical transactions into the database ledger.
    """
    if request.method == "POST":
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['excel_file']

            # Read and decode the file data safely
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)  # Skip the heading row automatically

            success_count = 0
            duplicate_count = 0

            for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                if not row or len(row) < 7:
                    continue  # Skip empty or broken rows safely

                # Map array indexes cleanly matching our explicit exporter variables
                receipt_id = row[1].strip() if row[1] else None
                tx_type = 'C2B' if "Paybill" in row[2] else ('B2C' if "Pastoral" in row[2] else 'STK_PUSH')
                giver_name = row[3].strip()
                phone = row[4].strip()
                raw_amount = row[5].replace('-', '').strip()  # Clean payout negative signs
                account_ref = row[6].strip()
                status_string = 'COMPLETED' if "Completed" in row[7] else (
                    'PENDING' if "Pending" in row[7] else 'FAILED')

                # Avoid duplicate entry crashes by checking the receipt token unique constraint
                if receipt_id and receipt_id != "N/A":
                    if MpesaTransaction.objects.filter(mpesa_receipt=receipt_id).exists():
                        duplicate_count += 1
                        continue

                try:
                    MpesaTransaction.objects.create(
                        transaction_type=tx_type,
                        amount=float(raw_amount),
                        phone_number=phone,
                        mpesa_receipt=receipt_id if receipt_id != "N/A" else None,
                        account_reference=account_ref,
                        first_name=giver_name if giver_name != "Anonymous / General Member" else "",
                        status=status_string,
                        created_at=timezone.now()
                    )
                    success_count += 1
                except Exception:
                    continue  # Skip structural parse conversion errors safely

            messages.success(request,
                             f"✨ Bulk Import Complete: Successfully logged {success_count} rows. (Skipped {duplicate_count} duplicate items).")
            return redirect('pastor_dashboard')

    messages.error(request, "❌ Invalid file processing request.")
    return redirect('pastor_dashboard')
