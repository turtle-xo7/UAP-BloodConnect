from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import CustomUserCreationForm, UserProfileForm, EmergencyBroadcastForm
from .models import UserProfile, CustomUser
from .decorators import advisor_required, president_required, moderator_required, super_admin_required


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    context = {'profile': profile}

    try:
        donor = request.user.donor
        from donors.models import DonationHistory, Achievement
        context['donor'] = donor
        context['recent_donations'] = DonationHistory.objects.filter(
            donor=donor
        ).order_by('-donation_date')[:5]
        context['achievements'] = Achievement.objects.filter(
            donor=donor
        ).order_by('-achieved_at')
        from requests.models import BloodRequest
        context['my_requests'] = BloodRequest.objects.filter(
            requester=request.user
        ).order_by('-created_at')[:3]
    except Exception:
        context['donor'] = None

    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})


# ─── Faculty Advisor Dashboard ───
@login_required
@advisor_required
def advisor_dashboard(request):
    from donors.models import DonationHistory, DonationDrive
    from requests.models import BloodRequest, EmergencyBroadcast, Notification

    # Verification queue — pending donations
    pending_donations = DonationHistory.objects.filter(
        verification_status='pending'
    ).select_related('donor__user', 'donor__blood_group').order_by('-created_at')

    # Moderation queue — pending blood requests
    pending_requests = BloodRequest.objects.filter(
        moderation_status='pending'
    ).select_related('requester', 'blood_group').order_by('-created_at')

    # Pending drives to approve
    pending_drives = DonationDrive.objects.filter(
        is_approved=False, status='upcoming'
    ).select_related('created_by').order_by('-created_at')

    # Pending broadcasts
    pending_broadcasts = EmergencyBroadcast.objects.filter(
        status='pending'
    ).select_related('created_by').order_by('-created_at')

    # Stats
    from donors.models import Donor
    context = {
        'pending_donations': pending_donations,
        'pending_requests': pending_requests,
        'pending_drives': pending_drives,
        'pending_broadcasts': pending_broadcasts,
        'pending_donation_count': pending_donations.count(),
        'pending_request_count': pending_requests.count(),
        'pending_drive_count': pending_drives.count(),
        'pending_broadcast_count': pending_broadcasts.count(),
        'total_donors': Donor.objects.count(),
        'total_users': CustomUser.objects.count(),
    }
    return render(request, 'accounts/advisor_dashboard.html', context)


@login_required
@advisor_required
def verify_donation(request, donation_id):
    from donors.models import DonationHistory
    donation = get_object_or_404(DonationHistory, id=donation_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            donation.verification_status = 'verified'
            donation.verified_by = request.user
            donation.verified_at = timezone.now()
            donation.save(update_fields=['verification_status', 'verified_by', 'verified_at'])

            # Now that it's verified, recount and award achievements.
            donor = donation.donor
            donor.total_donations = donor.donations.filter(
                verification_status='verified'
            ).count()
            donor.save(update_fields=['total_donations'])
            from donors.views import _award_achievements
            _award_achievements(donor)

            messages.success(request, f'Donation by {donation.donor.user.username} verified.')
        elif action == 'reject':
            reason = request.POST.get('rejection_reason', '').strip()
            donation.verification_status = 'rejected'
            donation.verified_by = request.user
            donation.verified_at = timezone.now()
            donation.rejection_reason = reason
            donation.save()
            messages.warning(request, f'Donation record rejected. Donor notified.')

    return redirect('advisor_dashboard')


@login_required
@moderator_required
def moderate_request(request, request_id):
    from requests.models import BloodRequest
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        note = request.POST.get('moderation_note', '').strip()
        if action == 'approve':
            blood_request.moderation_status = 'approved'
            blood_request.moderated_by = request.user
            blood_request.moderated_at = timezone.now()
            blood_request.moderation_note = note
            blood_request.save()
            # Now notify matching donors
            from requests.views import _notify_matching_donors
            _notify_matching_donors(blood_request)
            messages.success(request, 'Request approved and donors notified.')
        elif action == 'reject':
            blood_request.moderation_status = 'rejected'
            blood_request.status = 'closed'
            blood_request.moderated_by = request.user
            blood_request.moderated_at = timezone.now()
            blood_request.moderation_note = note
            blood_request.save()
            messages.warning(request, 'Request rejected.')

    return redirect('advisor_dashboard')


@login_required
@advisor_required
def approve_drive(request, drive_id):
    from donors.models import DonationDrive
    drive = get_object_or_404(DonationDrive, id=drive_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            drive.is_approved = True
            drive.approved_by = request.user
            drive.save(update_fields=['is_approved', 'approved_by'])
            messages.success(request, f'Drive "{drive.title}" approved.')
        elif action == 'reject':
            drive.status = 'cancelled'
            drive.save(update_fields=['status'])
            messages.warning(request, f'Drive "{drive.title}" rejected.')
    return redirect('advisor_dashboard')


@login_required
@advisor_required
def approve_broadcast(request, broadcast_id):
    from requests.models import EmergencyBroadcast, Notification
    broadcast = get_object_or_404(EmergencyBroadcast, id=broadcast_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            broadcast.status = 'approved'
            broadcast.approved_by = request.user
            broadcast.sent_at = timezone.now()
            broadcast.save()
            # Send notifications to all donors
            from donors.models import Donor
            donors = Donor.objects.select_related('user').all()
            for donor in donors:
                Notification.objects.create(
                    user=donor.user,
                    notification_type='new_request',
                    title=f'EMERGENCY: {broadcast.title}',
                    message=broadcast.message,
                    action_url='/requests/',
                )
            messages.success(request, f'Broadcast sent to {donors.count()} donors.')
        elif action == 'reject':
            broadcast.status = 'rejected'
            broadcast.approved_by = request.user
            broadcast.save(update_fields=['status', 'approved_by'])
            messages.warning(request, 'Broadcast rejected.')
    return redirect('advisor_dashboard')


# ─── Club President Dashboard ───
@login_required
@president_required
def president_dashboard(request):
    from donors.models import DonationDrive, Donor
    from requests.models import BloodRequest, EmergencyBroadcast

    drives = DonationDrive.objects.select_related('created_by').order_by('-date')[:10]
    pending_broadcasts = EmergencyBroadcast.objects.filter(
        status='pending', created_by=request.user
    ).order_by('-created_at')

    context = {
        'drives': drives,
        'pending_broadcasts': pending_broadcasts,
        'total_donors': Donor.objects.count(),
        'active_requests': BloodRequest.objects.filter(
            status='open', moderation_status='approved'
        ).count(),
    }
    return render(request, 'accounts/president_dashboard.html', context)


@login_required
@president_required
def create_broadcast(request):
    """Club president drafts an emergency broadcast; advisor must approve before send."""
    from requests.models import EmergencyBroadcast
    if request.method == 'POST':
        form = EmergencyBroadcastForm(request.POST)
        if form.is_valid():
            broadcast = form.save(commit=False)
            broadcast.created_by = request.user
            broadcast.status = 'pending'
            broadcast.save()
            messages.success(
                request,
                f'Broadcast "{broadcast.title}" submitted for faculty advisor approval.'
            )
            return redirect('president_dashboard')
    else:
        form = EmergencyBroadcastForm()
    return render(request, 'accounts/create_broadcast.html', {'form': form})


# ─── Role Management (Super Admin) ───
@login_required
@super_admin_required
def manage_roles(request):
    users = CustomUser.objects.all().order_by('role', 'username')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        target_user = get_object_or_404(CustomUser, id=user_id)
        if new_role in dict(CustomUser.ROLE_CHOICES):
            old_role = target_user.role
            target_user.role = new_role
            target_user.save(update_fields=['role'])
            messages.success(
                request,
                f'Role updated: {target_user.username} → {target_user.get_role_display()} (was {old_role})'
            )
            return redirect('manage_roles')

    context = {
        'users': users,
        'role_choices': CustomUser.ROLE_CHOICES,
    }
    return render(request, 'accounts/manage_roles.html', context)
