from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta
from .models import Donor, DonationHistory, Achievement, BloodGroup, DonationDrive, DriveRegistration
from .forms import DonorRegistrationForm, DonationHistoryForm, DonationDriveForm
from accounts.decorators import president_required, advisor_required, management_required


ACHIEVEMENT_MILESTONES = [
    (1,  'bronze',   'First Drop',      'You made your first blood donation! A hero is born.'),
    (3,  'bronze',   'Triple Saver',    'You have donated 3 times. The community thanks you!'),
    (5,  'silver',   'Regular Hero',    'Five donations — you are a regular lifesaver!'),
    (10, 'gold',     'Lifesaver',       'Ten donations — ten lives impacted. Pure gold!'),
    (25, 'platinum', 'Guardian Angel',  'Twenty-five donations — you are a guardian of life!'),
    (50, 'hero',     'Blood Hero',      'Fifty donations! You are a true Blood Hero of UAP.'),
]


def _award_achievements(donor):
    """Check milestones and award any new achievement badges."""
    from requests.models import Notification
    for count, badge_type, title, description in ACHIEVEMENT_MILESTONES:
        if donor.total_donations >= count:
            already_awarded = Achievement.objects.filter(donor=donor, title=title).exists()
            if not already_awarded:
                Achievement.objects.create(
                    donor=donor,
                    badge_type=badge_type,
                    title=title,
                    description=description,
                )
                Notification.objects.create(
                    user=donor.user,
                    notification_type='achievement',
                    title=f'Achievement Unlocked: {title}!',
                    message=description,
                    action_url='/donors/dashboard/',
                )


def _check_donation_eligibility(donor):
    """Return (eligible, days_remaining). Donors must wait 90 days between donations."""
    if not donor.last_donation_date:
        return True, 0
    next_eligible = donor.last_donation_date + timedelta(days=90)
    today = date.today()
    if today >= next_eligible:
        return True, 0
    return False, (next_eligible - today).days


@login_required
def donor_dashboard(request):
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        return redirect('donor_register')

    donation_history = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')[:5]
    achievements = Achievement.objects.filter(donor=donor).order_by('-achieved_at')
    eligible, days_remaining = _check_donation_eligibility(donor)

    # Update can_donate_again flag
    if donor.can_donate_again != eligible:
        donor.can_donate_again = eligible
        donor.save(update_fields=['can_donate_again'])

    context = {
        'donor': donor,
        'donation_history': donation_history,
        'achievements': achievements,
        'eligible': eligible,
        'days_remaining': days_remaining,
        'next_milestone': _next_milestone(donor.total_donations),
    }
    return render(request, 'donors/dashboard.html', context)


def _next_milestone(current):
    for count, badge_type, title, _ in ACHIEVEMENT_MILESTONES:
        if current < count:
            return {'count': count, 'badge_type': badge_type, 'title': title, 'remaining': count - current}
    return None


@login_required
def donor_register(request):
    if hasattr(request.user, 'donor'):
        messages.info(request, 'You are already registered as a donor.')
        return redirect('donor_dashboard')

    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            messages.success(request, 'Successfully registered as a donor! Thank you for joining the community.')
            return redirect('donor_dashboard')
    else:
        form = DonorRegistrationForm()

    return render(request, 'donors/register.html', {'form': form})


@login_required
def donor_directory(request):
    donors = Donor.objects.filter(availability_status='available').select_related('user', 'blood_group')
    blood_groups = BloodGroup.objects.all()

    blood_group_filter = request.GET.get('blood_group')
    location_filter = request.GET.get('location')

    if blood_group_filter:
        donors = donors.filter(blood_group__blood_type=blood_group_filter)
    if location_filter:
        donors = donors.filter(location=location_filter)

    context = {
        'donors': donors,
        'blood_groups': blood_groups,
        'selected_blood_group': blood_group_filter,
        'selected_location': location_filter,
    }
    return render(request, 'donors/directory.html', context)


@login_required
def add_donation_history(request):
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, 'You need to register as a donor first.')
        return redirect('donor_register')

    eligible, days_remaining = _check_donation_eligibility(donor)
    if not eligible:
        messages.warning(request, f'You need to wait {days_remaining} more days before your next donation (90-day interval required).')
        return redirect('donor_dashboard')

    if request.method == 'POST':
        form = DonationHistoryForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = donor
            donation.status = 'completed'
            donation.save()

            donor.total_donations += 1
            donor.last_donation_date = donation.donation_date
            donor.can_donate_again = False
            donor.save()

            # Award achievements
            _award_achievements(donor)

            messages.success(request, 'Donation recorded! Thank you for saving lives.')
            return redirect('donor_dashboard')
    else:
        form = DonationHistoryForm()

    return render(request, 'donors/add_donation.html', {'form': form})


@login_required
def donation_history(request):
    try:
        donor = Donor.objects.get(user=request.user)
        donations = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')
        return render(request, 'donors/donation_history.html', {'donations': donations, 'donor': donor})
    except Donor.DoesNotExist:
        messages.error(request, 'You need to register as a donor first.')
        return redirect('donor_register')


def leaderboard(request):
    top_donors = Donor.objects.select_related('user', 'blood_group').order_by('-total_donations')[:20]
    blood_groups = BloodGroup.objects.all()
    blood_group_filter = request.GET.get('blood_group')

    if blood_group_filter:
        top_donors = Donor.objects.filter(
            blood_group__blood_type=blood_group_filter
        ).select_related('user', 'blood_group').order_by('-total_donations')[:20]

    context = {
        'top_donors': top_donors,
        'blood_groups': blood_groups,
        'selected_blood_group': blood_group_filter,
    }
    return render(request, 'donors/leaderboard.html', context)


@login_required
def update_availability(request):
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, 'You are not registered as a donor.')
        return redirect('home')

    if request.method == 'POST':
        status = request.POST.get('availability_status')
        if status in ['available', 'busy', 'unavailable']:
            donor.availability_status = status
            donor.save(update_fields=['availability_status'])
            messages.success(request, f'Availability updated to: {status.title()}')
    return redirect('donor_dashboard')


# ─── Donation Drive Views ───

def drive_list(request):
    drives = DonationDrive.objects.filter(
        is_approved=True
    ).select_related('created_by').prefetch_related('target_blood_groups').order_by('-date')

    status_filter = request.GET.get('status')
    if status_filter:
        drives = drives.filter(status=status_filter)

    # Which drives has the current user registered for?
    registered_ids = set()
    if request.user.is_authenticated:
        try:
            donor = request.user.donor
            registered_ids = set(
                DriveRegistration.objects.filter(donor=donor).values_list('drive_id', flat=True)
            )
        except Exception:
            pass

    context = {
        'drives': drives,
        'registered_ids': registered_ids,
        'status_filter': status_filter,
    }
    return render(request, 'donors/drive_list.html', context)


def drive_detail(request, drive_id):
    drive = get_object_or_404(DonationDrive, id=drive_id)
    registrations = DriveRegistration.objects.filter(drive=drive).select_related('donor__user')

    is_registered = False
    if request.user.is_authenticated:
        try:
            donor = request.user.donor
            is_registered = DriveRegistration.objects.filter(drive=drive, donor=donor).exists()
        except Exception:
            pass

    context = {
        'drive': drive,
        'registrations': registrations,
        'is_registered': is_registered,
    }
    return render(request, 'donors/drive_detail.html', context)


@login_required
@president_required
def create_drive(request):
    if request.method == 'POST':
        form = DonationDriveForm(request.POST)
        if form.is_valid():
            drive = form.save(commit=False)
            drive.created_by = request.user
            drive.status = 'upcoming'
            drive.save()
            form.save_m2m()
            messages.success(request, f'Drive "{drive.title}" created and submitted for advisor approval.')
            return redirect('drive_detail', drive_id=drive.id)
    else:
        form = DonationDriveForm()
    return render(request, 'donors/create_drive.html', {'form': form})


@login_required
def register_for_drive(request, drive_id):
    drive = get_object_or_404(DonationDrive, id=drive_id, is_approved=True)

    try:
        donor = request.user.donor
    except Exception:
        messages.error(request, 'You must be a registered donor to sign up for a drive.')
        return redirect('drive_detail', drive_id=drive_id)

    if drive.status not in ('upcoming', 'active'):
        messages.warning(request, 'This drive is no longer accepting registrations.')
        return redirect('drive_detail', drive_id=drive_id)

    _, created = DriveRegistration.objects.get_or_create(drive=drive, donor=donor)
    if created:
        messages.success(request, f'Registered for "{drive.title}"! See you there.')
    else:
        messages.info(request, 'You are already registered for this drive.')
    return redirect('drive_detail', drive_id=drive_id)


@login_required
def unregister_from_drive(request, drive_id):
    drive = get_object_or_404(DonationDrive, id=drive_id)
    try:
        donor = request.user.donor
        reg = DriveRegistration.objects.get(drive=drive, donor=donor)
        reg.delete()
        messages.success(request, 'Registration cancelled.')
    except Exception:
        messages.warning(request, 'No registration found.')
    return redirect('drive_detail', drive_id=drive_id)


@login_required
@management_required
def mark_attendance(request, drive_id, registration_id):
    """Mark a donor as having donated at a drive."""
    drive = get_object_or_404(DonationDrive, id=drive_id)
    reg = get_object_or_404(DriveRegistration, id=registration_id, drive=drive)

    if request.method == 'POST':
        reg.donated = True
        reg.save(update_fields=['donated'])
        messages.success(request, f'{reg.donor.user.username} marked as donated.')
    return redirect('drive_detail', drive_id=drive_id)
