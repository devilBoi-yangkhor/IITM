from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import User  # IMPORT YOUR CUSTOM USER MODEL - THIS IS THE FIX!
import json
from django.urls import reverse

def home(request):
    """Home page view"""
    return render(request, 'training_institute_app/home.html')

def about(request):
    return render(request, 'training_institute_app/about.html')

def courses(request):
    return render(request, 'training_institute_app/courses.html')

def courses_details(request):
    context = {
        'user': request.user,
    }
    return render(request, 'training_institute_app/courses/courses_details.html', context)

@login_required
@csrf_exempt
def enroll_course(request):
    """Handle course enrollment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            course_name = data.get('course_name', 'ICT & Software Development Program')
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully enrolled in {course_name}',
                'user': request.user.username
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

def contact(request):
    return render(request, 'training_institute_app/contact.html')

def login_view(request):
    return render(request, 'training_institute_app/login.html')

def signin(request):
    """Handle sign in / login functionality"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful
            auth_login(request, user)
            
            # Check if remember me is checked
            if not request.POST.get('remember'):
                request.session.set_expiry(0)  # Session expires when browser closes
            
            return JsonResponse({
                'success': True,
                'message': f'Welcome back, {user.username}!',
                'redirect_url': '/dashboard/'
            })
        else:
            # Login failed
            return JsonResponse({
                'success': False,
                'message': 'Invalid username or password. Please try again.'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

def signup(request):
    """Handle sign up / registration functionality"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        
        # Check if passwords match
        if password != password2:
            return JsonResponse({
                'success': False,
                'message': 'Passwords do not match!'
            }, status=400)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username already taken. Please choose another.'
            }, status=400)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email already registered. Please use another email.'
            }, status=400)
        
        # Create new user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.save()
            
            # REMOVED auto login - user must sign in manually
            # Just return success with redirect to login page
            
            return JsonResponse({
                'success': True,
                'message': f'Account created successfully! Please sign in to continue.',
                'redirect_url': '/login/'
            })
        except Exception as e:
            print(f"Error creating user: {str(e)}")  # For debugging
            return JsonResponse({
                'success': False,
                'message': 'Something went wrong. Please try again.'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

def google_callback(request):
    """Handle Google OAuth callback"""
    from allauth.socialaccount.models import SocialApp
    import requests
    
    code = request.GET.get('code')
    if not code:
        return redirect('/login/')
    
    try:
        app = SocialApp.objects.get(provider='google')
        
        # Exchange code for token
        token_url = 'https://oauth2.googleapis.com/token'
        redirect_uri = request.build_absolute_uri(reverse('google_callback'))
        
        data = {
            'code': code,
            'client_id': app.client_id,
            'client_secret': app.secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        
        response = requests.post(token_url, data=data)
        token_data = response.json()
        
        if 'access_token' not in token_data:
            return redirect('/login/')
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_data = user_response.json()
        
        if 'email' in user_data:
            email = user_data['email']
            username = user_data.get('email').split('@')[0]
            full_name = user_data.get('name', username)
            google_picture = user_data.get('picture', '')
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'full_name': full_name,
                    'google_picture': google_picture,  # Save to your custom field
                    'is_active_user': True,
                }
            )
            
            if not created:
                # Update existing user's Google picture
                if google_picture:
                    user.google_picture = google_picture
                    user.save()
            
            if created:
                user.set_unusable_password()
                user.save()
            
            auth_login(request, user)
            return redirect('/dashboard/')
        
        return redirect('/login/')
        
    except Exception as e:
        print(f"Callback error: {e}")
        return redirect('/login/')
    
def google_login_direct(request):
    """Direct Google login - skips the intermediate page"""
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
    from allauth.socialaccount.providers.oauth2.client import OAuth2Client
    from allauth.socialaccount.models import SocialApp
    from django.urls import reverse
    from django.http import HttpResponseRedirect
    
    # Get the Google app
    try:
        app = SocialApp.objects.get(provider='google')
        
        # Build the Google OAuth URL directly
        client = OAuth2Client(request, app.client_id, app.secret, app.secret)
        redirect_uri = request.build_absolute_uri(reverse('google_callback'))
        authorization_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        
        params = {
            'client_id': app.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'profile email',
            'access_type': 'online',
        }
        
        from urllib.parse import urlencode
        auth_url = f"{authorization_url}?{urlencode(params)}"
        
        return HttpResponseRedirect(auth_url)
    except Exception as e:
        print(f"Error: {e}")
        return redirect('/login/')

def logout_view(request):
    """Handle logout"""
    auth_logout(request)
    return redirect('/')

# Dashboard Views - PROTECTED - only accessible after successful sign in
@login_required(login_url='/login/')
def dashboard(request):
    # Get Google profile picture from social account if exists
    google_picture = None
    try:
        from allauth.socialaccount.models import SocialAccount
        social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if social_account:
            google_picture = social_account.get_avatar_url()
    except:
        pass
    
    context = {
        'user': request.user,
        'user_full_name': request.user.get_full_name() or request.user.username,
        'user_email': request.user.email,
        'user_username': request.user.username,
        'user_joined': request.user.date_joined,
        'user_last_login': request.user.last_login,
        'profile_picture': request.user.profile_picture.url if request.user.profile_picture else None,
        'google_picture': google_picture or request.user.google_picture,  # Use social account picture
    }
    return render(request, 'training_institute_app/dashboard/index.html', context)


#masterManagement Views
@login_required(login_url='/login/')
def user_management(request):
    # Handle POST request for editing/deleting user
    if request.method == 'POST':
        # Handle Delete
        if 'delete_user_id' in request.POST:
            user_id = request.POST.get('delete_user_id')
            try:
                user = User.objects.get(id=user_id)
                # Don't allow deleting yourself
                if user.id != request.user.id:
                    username = user.username
                    user.delete()
                    messages.success(request, f'User "{username}" deleted successfully!')
                else:
                    messages.error(request, 'You cannot delete your own account!')
            except User.DoesNotExist:
                messages.error(request, 'User not found!')
            return redirect('user_management')
        
        # Handle Edit
        user_id = request.POST.get('user_id')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        is_student = request.POST.get('is_student') == 'on'
        is_teacher = request.POST.get('is_teacher') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            user = User.objects.get(id=user_id)
            user.full_name = full_name
            user.email = email
            user.phone_number = phone_number
            user.is_student = is_student
            user.is_teacher = is_teacher
            user.is_active = is_active
            user.save()
            
            messages.success(request, f'User "{user.username}" updated successfully!')
        except User.DoesNotExist:
            messages.error(request, 'User not found!')
        
        return redirect('user_management')
    
    # GET request - show users (MUST return response)
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
    }
    return render(request, 'training_institute_app/dashboard/master/user-management.html', context)