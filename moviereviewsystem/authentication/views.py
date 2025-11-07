from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages


@require_http_methods(["POST"])
def login_view(request):
    """Handle modal login via AJAX"""
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    # Authenticate user
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)

        if is_ajax:
            return JsonResponse({
                'success': True,
                'redirect': request.POST.get('next', '/'),
                'message': f'Welcome back, {username}!'
            })
        else:
            messages.success(request, f'Welcome back, {username}!')
            return redirect(request.POST.get('next', 'main'))
    else:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password. Please try again.'
            })
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('main')


@require_http_methods(["POST"])
def signup_view(request):
    """Handle modal signup via AJAX"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')

    # Validation
    errors = []

    if not username:
        errors.append('Username is required.')
    elif len(username) < 3:
        errors.append('Username must be at least 3 characters.')
    elif User.objects.filter(username=username).exists():
        errors.append('Username already taken.')

    if not email:
        errors.append('Email is required.')
    elif User.objects.filter(email=email).exists():
        errors.append('Email already registered.')

    if not password1:
        errors.append('Password is required.')
    elif len(password1) < 8:
        errors.append('Password must be at least 8 characters.')

    if password1 != password2:
        errors.append('Passwords do not match.')

    # If there are errors, return them
    if errors:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': errors
            })
        else:
            for error in errors:
                messages.error(request, error)
            return redirect('main')

    # Create user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        login(request, user)

        if is_ajax:
            return JsonResponse({
                'success': True,
                'redirect': request.POST.get('next', '/'),
                'message': f'Welcome, {username}! Your account has been created.'
            })
        else:
            messages.success(request, f'Welcome, {username}!')
            return redirect('main')

    except Exception as e:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': ['Error creating account. Please try again.']
            })
        else:
            messages.error(request, 'Error creating account.')
            return redirect('main')


def logout_view(request):
    """Handle logout"""
    username = request.user.username if request.user.is_authenticated else None
    logout(request)

    if username:
        messages.success(request, f'Goodbye, {username}! You have been logged out.')

    return redirect('main')