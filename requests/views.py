from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from .models import BloodRequest, RequestResponse, Notification, Feedback
from .forms import BloodRequestForm, RequestResponseForm, FeedbackForm
from donors.models import Donor, BloodGroup


def _notify_matching_donors(blood_request):
    """Create notifications for donors whose blood type matches this request."""
    matching_donors = Donor.objects.filter(
        blood_group=blood_request.blood_group,
        availability_status='available',
    ).select_related('user')

    for donor in matching_donors:
        if donor.user != blood_request.requester:
            Notification.objects.get_or_create(
                user=donor.user,
                notification_type='new_request',
                title=f'New Blood Request: {blood_request.blood_group} Needed',
                defaults={
                    'message': (
                        f'{blood_request.blood_group.blood_type} blood is urgently needed for '
                        f'{blood_request.patient_name} at {blood_request.get_location_display()}. '
                        f'Urgency: {blood_request.get_urgency_display()}.'
                    ),
                    'action_url': f'/requests/{blood_request.id}/',
                }
            )


@login_required
def create_request(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST, request.FILES)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()

            _notify_matching_donors(blood_request)

            messages.success(request, 'Blood request created! Matching donors have been notified.')
            return redirect('request_detail', request_id=blood_request.id)
    else:
        form = BloodRequestForm()

    return render(request, 'requests/create_request.html', {'form': form})


@login_required
def request_list(request):
    all_requests = BloodRequest.objects.all().select_related('requester', 'blood_group').order_by('-created_at')

    blood_group_filter = request.GET.get('blood_group')
    status_filter = request.GET.get('status')
    urgency_filter = request.GET.get('urgency')
    location_filter = request.GET.get('location')

    if blood_group_filter:
        all_requests = all_requests.filter(blood_group__blood_type=blood_group_filter)
    if status_filter:
        all_requests = all_requests.filter(status=status_filter)
    if urgency_filter:
        all_requests = all_requests.filter(urgency=urgency_filter)
    if location_filter:
        all_requests = all_requests.filter(location=location_filter)

    context = {
        'requests': all_requests,
        'blood_groups': BloodGroup.objects.all(),
    }
    return render(request, 'requests/request_list.html', context)


@login_required
def request_detail(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    user_response = None
    if hasattr(request.user, 'donor'):
        user_response = RequestResponse.objects.filter(
            blood_request=blood_request,
            donor=request.user.donor
        ).first()

    responses = RequestResponse.objects.filter(
        blood_request=blood_request
    ).select_related('donor__user', 'donor__blood_group')

    if request.method == 'POST' and hasattr(request.user, 'donor'):
        form = RequestResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.blood_request = blood_request
            response.donor = request.user.donor
            response.save()

            Notification.objects.create(
                user=blood_request.requester,
                notification_type='response',
                title=f'Donor Responded to Your Request',
                message=f'{request.user.get_full_name() or request.user.username} has responded to your {blood_request.blood_group.blood_type} blood request.',
                action_url=f'/requests/{blood_request.id}/',
            )

            messages.success(request, 'Your response has been submitted! The requester will be notified.')
            return redirect('request_detail', request_id=request_id)
    else:
        form = RequestResponseForm()

    context = {
        'blood_request': blood_request,
        'responses': responses,
        'user_response': user_response,
        'form': form,
        'can_respond': hasattr(request.user, 'donor') and not user_response,
    }
    return render(request, 'requests/request_detail.html', context)


@login_required
def my_requests(request):
    my_requests_qs = BloodRequest.objects.filter(
        requester=request.user
    ).select_related('blood_group').order_by('-created_at')
    return render(request, 'requests/my_requests.html', {'my_requests': my_requests_qs})


@login_required
def respond_to_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id)

    if not hasattr(request.user, 'donor'):
        messages.error(request, 'You need to be registered as a donor to respond to requests.')
        return redirect('donor_register')

    if RequestResponse.objects.filter(blood_request=blood_request, donor=request.user.donor).exists():
        messages.info(request, 'You have already responded to this request.')
        return redirect('request_detail', request_id=request_id)

    if request.method == 'POST':
        form = RequestResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.blood_request = blood_request
            response.donor = request.user.donor
            response.save()
            messages.success(request, 'Thank you for responding to this blood request!')
            return redirect('request_detail', request_id=request_id)
    else:
        form = RequestResponseForm()

    return render(request, 'requests/respond.html', {'form': form, 'blood_request': blood_request})


def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your feedback! We appreciate your input.')
            return redirect('home')
    else:
        form = FeedbackForm()

    return render(request, 'requests/feedback.html', {'form': form})


def feedback_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff members only.')
        return redirect('home')

    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'requests/feedback_list.html', {'feedbacks': feedbacks})


@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    unread = user_notifications.filter(is_read=False)
    context = {
        'notifications': user_notifications,
        'unread_count': unread.count(),
    }
    return render(request, 'requests/notifications.html', context)


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    if notif.action_url:
        return redirect(notif.action_url)
    return redirect('notifications')


@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')
