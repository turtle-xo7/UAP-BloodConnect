from django.shortcuts import render
from django.db.models import Count, Sum
from donors.models import Donor, BloodGroup, DonationHistory
from requests.models import BloodRequest, Notification


def home(request):
    blood_groups = BloodGroup.objects.all()
    total_donors = Donor.objects.count()
    active_requests = BloodRequest.objects.filter(status='open').count()
    fulfilled_requests = BloodRequest.objects.filter(status='fulfilled').count()
    total_donations = DonationHistory.objects.filter(status='completed').count()

    # Blood inventory: count available donors per blood type
    blood_inventory = []
    max_donors = 1
    for bg in blood_groups:
        count = Donor.objects.filter(blood_group=bg, availability_status='available').count()
        blood_inventory.append({'blood_type': bg.blood_type, 'count': count})
        if count > max_donors:
            max_donors = count

    # Top 5 donors by total_donations
    top_donors = Donor.objects.select_related('user', 'blood_group').order_by('-total_donations')[:5]

    # Urgent / critical requests
    urgent_requests = BloodRequest.objects.filter(
        status='open',
        urgency__in=['critical', 'high']
    ).select_related('blood_group', 'requester').order_by('-urgency', '-created_at')[:4]

    lives_saved = fulfilled_requests * 3  # industry standard: 1 donation = ~3 lives

    context = {
        'total_donors': total_donors,
        'active_requests': active_requests,
        'total_donations': total_donations,
        'fulfilled_requests': fulfilled_requests,
        'lives_saved': lives_saved,
        'blood_groups': blood_groups,
        'blood_inventory': blood_inventory,
        'max_donors': max_donors,
        'top_donors': top_donors,
        'urgent_requests': urgent_requests,
    }
    return render(request, 'home.html', context)


def about(request):
    return render(request, 'about.html')


def eligibility_checker(request):
    return render(request, 'eligibility_checker.html')


def blood_type_education(request):
    blood_types = [
        {
            'type': 'O-',
            'label': 'Universal Donor',
            'color': '#854D0E',
            'bg': '#FEFCE8',
            'border': '#FEF08A',
            'can_give_to': 'All blood types',
            'can_receive': 'O- only',
            'facts': ['Rarest negative type', 'Used in emergencies', 'Hospitals always need O-'],
            'frequency': '7%',
        },
        {
            'type': 'O+',
            'label': 'Most Common',
            'color': '#6D28D9',
            'bg': '#F5F3FF',
            'border': '#DDD6FE',
            'can_give_to': 'O+, A+, B+, AB+',
            'can_receive': 'O+, O-',
            'facts': ['Most common type', '38% of people have O+', 'High demand for trauma'],
            'frequency': '38%',
        },
        {
            'type': 'A+',
            'label': 'Very Common',
            'color': '#991B1B',
            'bg': '#FEE2E2',
            'border': '#FECACA',
            'can_give_to': 'A+, AB+',
            'can_receive': 'A+, A-, O+, O-',
            'facts': ['Second most common', '28% of population', 'Good for plasma donation'],
            'frequency': '28%',
        },
        {
            'type': 'A-',
            'label': 'Rare',
            'color': '#9A3412',
            'bg': '#FFF7ED',
            'border': '#FED7AA',
            'can_give_to': 'A+, A-, AB+, AB-',
            'can_receive': 'A-, O-',
            'facts': ['Only 6% of people', 'Valuable for multiple types', 'Great plasma donor'],
            'frequency': '6%',
        },
        {
            'type': 'B+',
            'label': 'Common',
            'color': '#166534',
            'bg': '#F0FDF4',
            'border': '#BBF7D0',
            'can_give_to': 'B+, AB+',
            'can_receive': 'B+, B-, O+, O-',
            'facts': ['More common in South Asia', '9% of people globally', 'Important for platelets'],
            'frequency': '9%',
        },
        {
            'type': 'B-',
            'label': 'Rare',
            'color': '#1E40AF',
            'bg': '#EFF6FF',
            'border': '#BFDBFE',
            'can_give_to': 'B+, B-, AB+, AB-',
            'can_receive': 'B-, O-',
            'facts': ['Only 2% of people', 'Valuable negative type', 'Needed for sickle cell'],
            'frequency': '2%',
        },
        {
            'type': 'AB+',
            'label': 'Universal Recipient',
            'color': '#7E22CE',
            'bg': '#FDF4FF',
            'border': '#F5D0FE',
            'can_give_to': 'AB+ only',
            'can_receive': 'All blood types',
            'facts': ['Universal plasma donor', 'Only 3% of people', 'Can receive any blood type'],
            'frequency': '3%',
        },
        {
            'type': 'AB-',
            'label': 'Rarest Type',
            'color': '#065F46',
            'bg': '#F0FDFA',
            'border': '#99F6E4',
            'can_give_to': 'AB+, AB-',
            'can_receive': 'AB-, A-, B-, O-',
            'facts': ['Rarest blood type', 'Less than 1%', 'Universal plasma donor'],
            'frequency': '<1%',
        },
    ]
    # Compatibility matrix: rows = recipient, cols = donor [O-, O+, A-, A+, B-, B+, AB-, AB+]
    compatibility_matrix = [
        {'type': 'O-',  'can_receive': [True,  False, False, False, False, False, False, False]},
        {'type': 'O+',  'can_receive': [True,  True,  False, False, False, False, False, False]},
        {'type': 'A-',  'can_receive': [True,  False, True,  False, False, False, False, False]},
        {'type': 'A+',  'can_receive': [True,  True,  True,  True,  False, False, False, False]},
        {'type': 'B-',  'can_receive': [True,  False, False, False, True,  False, False, False]},
        {'type': 'B+',  'can_receive': [True,  True,  False, False, True,  True,  False, False]},
        {'type': 'AB-', 'can_receive': [True,  False, True,  False, True,  False, True,  False]},
        {'type': 'AB+', 'can_receive': [True,  True,  True,  True,  True,  True,  True,  True ]},
    ]
    return render(request, 'blood_type_education.html', {
        'blood_types': blood_types,
        'compatibility_rows': compatibility_matrix,
    })
