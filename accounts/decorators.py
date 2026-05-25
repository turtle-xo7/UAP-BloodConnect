from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


# Role hierarchy — each role inherits all permissions of roles below it
ROLE_HIERARCHY = {
    'super_admin':      9,
    'faculty_advisor':  8,
    'medical_verifier': 7,
    'club_president':   6,
    'club_secretary':   5,
    'club_moderator':   4,
    'camp_coordinator': 3,
    'donor':            2,
    'student':          1,
}


def get_user_level(user):
    if user.is_superuser:
        return 9
    return ROLE_HIERARCHY.get(user.role, 1)


def role_required(*required_roles, redirect_url='home', message=None):
    """
    Decorator that checks if the logged-in user has one of the required roles.
    Roles are checked with hierarchy: a higher-level role can always do what
    a lower-level role can.

    Usage:
        @role_required('faculty_advisor', 'medical_verifier')
        def my_view(request): ...

        @role_required('club_president')
        def president_only_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            required_levels = [ROLE_HIERARCHY.get(r, 0) for r in required_roles]
            user_level = get_user_level(request.user)

            # Allow if user's level is >= any required role's level (OR logic)
            if any(user_level >= lvl for lvl in required_levels):
                return view_func(request, *args, **kwargs)

            msg = message or "You don't have permission to access this page."
            messages.error(request, msg)
            return redirect(redirect_url)

        return _wrapped
    return decorator


# ─── Convenience decorators ───

def super_admin_required(view_func):
    return role_required('super_admin')(view_func)


def advisor_required(view_func):
    return role_required('faculty_advisor')(view_func)


def verifier_required(view_func):
    return role_required('medical_verifier')(view_func)


def president_required(view_func):
    return role_required('club_president')(view_func)


def secretary_required(view_func):
    return role_required('club_secretary')(view_func)


def moderator_required(view_func):
    return role_required('club_moderator')(view_func)


def management_required(view_func):
    """Any role above student/donor."""
    return role_required('camp_coordinator')(view_func)
