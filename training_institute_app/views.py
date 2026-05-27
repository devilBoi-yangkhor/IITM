from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import *
import json
from django.urls import reverse
from django.db import models

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
    if request.user.is_authenticated:
        return redirect('/dashboard/')
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
                    'google_picture': google_picture,
                    'is_active_user': True,
                    'is_active': True,  # ✅ Add this
                }
            )
            
            if not created:
                if google_picture:
                    user.google_picture = google_picture
                user.is_active = True  # ✅ Ensure existing users are active too
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
    # Handle POST request for adding/editing users (NO DELETE HERE)
    if request.method == 'POST':
        # Check if this is an edit FIRST - by checking for item_id or form_type='edit'
        item_id = request.POST.get('item_id')
        form_type = request.POST.get('form_type')
        
        # IMPORTANT: Check for edit FIRST before checking for add
        if form_type == 'edit' or item_id:
            # Get the actual user ID
            actual_user_id = item_id
            
            if not actual_user_id:
                return JsonResponse({'success': False, 'message': 'No user ID provided for edit!'})
            
            # Get fields
            full_name = request.POST.get('full_name', '')
            email = request.POST.get('email', '')
            phone_number = request.POST.get('phone_number', '')
            
            # Handle checkbox values (they come as 'true' or 'on' from different form types)
            is_student_raw = request.POST.get('is_student', 'false')
            is_teacher_raw = request.POST.get('is_teacher', 'false')
            is_active_raw = request.POST.get('is_active', 'false')
            
            # Convert to boolean
            is_student = is_student_raw in ['true', 'on', 'True', '1', True]
            is_teacher = is_teacher_raw in ['true', 'on', 'True', '1', True]
            is_active = is_active_raw in ['true', 'on', 'True', '1', True]
            
            try:
                user = User.objects.get(id=actual_user_id)
                user.full_name = full_name
                user.email = email
                user.phone_number = phone_number
                user.is_student = is_student
                user.is_teacher = is_teacher
                user.is_active = is_active
                user.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'User "{user.username}" updated successfully!'})
                else:
                    messages.success(request, f'User "{user.username}" updated successfully!')
                    return redirect('user_management')
            except User.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'User not found with ID: {actual_user_id}'})
                else:
                    messages.error(request, 'User not found!')
                    return redirect('user_management')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
                else:
                    messages.error(request, f'Error: {str(e)}')
                    return redirect('user_management')
        
        # Handle Add new user (ONLY if not edit)
        else:
            username = request.POST.get('username')
            full_name = request.POST.get('full_name', '')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number', '')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate required fields
            if not username:
                return JsonResponse({'success': False, 'message': 'Username is required!'})
            
            if not email:
                return JsonResponse({'success': False, 'message': 'Email is required!'})
            
            if not password:
                return JsonResponse({'success': False, 'message': 'Password is required!'})
            
            # Check if passwords match
            if password != confirm_password:
                return JsonResponse({'success': False, 'message': 'Passwords do not match!'})
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'Username "{username}" already exists!'})
                else:
                    messages.error(request, f'Username "{username}" already exists!')
                    return redirect('user_management')
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'Email "{email}" already exists!'})
                else:
                    messages.error(request, f'Email "{email}" already exists!')
                    return redirect('user_management')
            
            # Create new user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.full_name = full_name
                user.phone_number = phone_number
                user.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'User "{username}" created successfully!'})
                else:
                    messages.success(request, f'User "{username}" created successfully!')
                    return redirect('user_management')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'Error creating user: {str(e)}'})
                else:
                    messages.error(request, f'Error creating user: {str(e)}')
                    return redirect('user_management')
    
    # GET request - show users
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
    }
    return render(request, 'training_institute_app/dashboard/master/user-management.html', context)

# ADD THIS NEW FUNCTION - Separate endpoint for user deletion
@login_required(login_url='/login/')
def delete_user(request):
    """Handle user deletion separately"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        # Don't allow deleting yourself
        if str(user_id) == str(request.user.id):
            return JsonResponse({'success': False, 'message': 'You cannot delete your own account!'})
        
        try:
            user = User.objects.get(id=user_id)
            username = user.username
            user.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'User "{username}" deleted successfully!'
                })
            else:
                messages.success(request, f'User "{username}" deleted successfully!')
                return redirect('user_management')
                
        except User.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'User not found!'})
            else:
                messages.error(request, 'User not found!')
                return redirect('user_management')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
            else:
                messages.error(request, f'Error deleting user: {str(e)}')
                return redirect('user_management')
    
    # If not POST, redirect to user management
    return redirect('user_management')

@login_required(login_url='/login/')
def role_management(request):
    # Handle POST request for adding/editing roles (NO DELETE HERE)
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        # Handle Add/Edit only - DELETE removed from here
        role_id = request.POST.get('role_id')
        role_name = request.POST.get('role_name')
        description = request.POST.get('description')
        
        if role_id and role_id != '':  # Edit existing role
            try:
                role = Role.objects.get(id=role_id)
                # Check if name already exists BUT exclude current role
                if Role.objects.filter(name__iexact=role_name).exclude(id=role_id).exists():
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': f'Role "{role_name}" already exists!'})
                    else:
                        messages.error(request, f'Role "{role_name}" already exists!')
                        return redirect('role_management')
                
                # Update role
                role.name = role_name
                role.description = description
                role.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'Role "{role_name}" updated successfully!'})
                else:
                    messages.success(request, f'Role "{role_name}" updated successfully!')
                    return redirect('role_management')
            except Role.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Role not found!'})
                else:
                    messages.error(request, 'Role not found!')
                    return redirect('role_management')
        else:  # Add new role
            # Check if role name already exists
            if Role.objects.filter(name__iexact=role_name).exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'Role "{role_name}" already exists!'})
                else:
                    messages.error(request, f'Role "{role_name}" already exists!')
                    return redirect('role_management')
            else:
                Role.objects.create(name=role_name, description=description)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'Role "{role_name}" created successfully!'})
                else:
                    messages.success(request, f'Role "{role_name}" created successfully!')
                    return redirect('role_management')
    
    # GET request - show all roles with user counts
    roles = Role.objects.all().annotate(
        user_count=models.Count('user')
    ).order_by('name')
    
    context = {
        'roles': roles,
    }
    return render(request, 'training_institute_app/dashboard/master/user-role.html', context)


# NEW DELETE FUNCTION - Separate endpoint for delete operations
@login_required(login_url='/login/')
def delete_role(request):
    """Handle role deletion separately"""
    if request.method == 'POST':
        role_id = request.POST.get('delete_role_id')
        
        try:
            role = Role.objects.get(id=role_id)
            role_name = role.name
            
            # Check if role has users assigned
            user_count = role.user_set.count()
            
            # Perform the deletion
            role.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'Role "{role_name}" deleted successfully!',
                    'user_count': user_count
                })
            else:
                messages.success(request, f'Role "{role_name}" deleted successfully!')
                return redirect('role_management')
                
        except Role.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Role not found!'})
            else:
                messages.error(request, 'Role not found!')
                return redirect('role_management')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
            else:
                messages.error(request, f'Error deleting role: {str(e)}')
                return redirect('role_management')
    
    # If not POST, redirect to role management
    return redirect('role_management')

@login_required(login_url='/login/')
def course_management(request):
    # Handle POST request for adding/editing/deleting courses
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        # Handle Delete
        if form_type == 'delete':
            course_id = request.POST.get('delete_course_id')
            try:
                course = Course.objects.get(id=course_id)
                course_name = course.course_name
                course.delete()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'Course "{course_name}" deleted successfully!'})
                else:
                    messages.success(request, f'Course "{course_name}" deleted successfully!')
                    return redirect('course_management')
            except Course.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Course not found!'})
                else:
                    messages.error(request, 'Course not found!')
                    return redirect('course_management')
        
        # Handle Add/Edit
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course_name')
        description = request.POST.get('description')
        credits = request.POST.get('credits', 3)
        duration_weeks = request.POST.get('duration_weeks', 12)
        schedule_type = request.POST.get('schedule_type', 'Flexible')
        batch_size = request.POST.get('batch_size', '15-20')
        course_fee = request.POST.get('course_fee', 0)
        max_students = request.POST.get('max_students', 30)
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        category_id = request.POST.get('category_id')
        department_id = request.POST.get('department_id')
        instructor_id = request.POST.get('instructor_id')
        
        # New fields from the form
        certification_provided = request.POST.get('certification_provided', 'false') == 'true'
        certification_name = request.POST.get('certification_name', '')
        enrollment_open = request.POST.get('enrollment_open', 'false') == 'true'
        enrollment_deadline = request.POST.get('enrollment_deadline')
        program_badge = request.POST.get('program_badge', '')
        program_badge_icon = request.POST.get('program_badge_icon', 'fas fa-laptop-code')
        hero_title = request.POST.get('hero_title', '')
        hero_subtitle = request.POST.get('hero_subtitle', '')
        
        # Parse JSON data for repeatable sections
        what_you_will_master = []
        who_should_attend = []
        program_structure = []
        
        try:
            if request.POST.get('what_you_will_master'):
                what_you_will_master = json.loads(request.POST.get('what_you_will_master'))
        except json.JSONDecodeError:
            what_you_will_master = []
        
        try:
            if request.POST.get('who_should_attend'):
                who_should_attend = json.loads(request.POST.get('who_should_attend'))
        except json.JSONDecodeError:
            who_should_attend = []
        
        try:
            if request.POST.get('program_structure'):
                program_structure = json.loads(request.POST.get('program_structure'))
        except json.JSONDecodeError:
            program_structure = []
        
        if course_id and course_id != '':  # Edit existing course
            try:
                course = Course.objects.get(id=course_id)
                
                # Update basic fields
                course.course_name = course_name
                course.description = description
                course.credits = credits
                course.duration_weeks = duration_weeks
                course.schedule_type = schedule_type
                course.batch_size = batch_size
                course.course_fee = course_fee
                course.max_students = max_students
                
                # Update new fields
                course.certification_provided = certification_provided
                course.certification_name = certification_name
                course.enrollment_open = enrollment_open
                course.program_badge = program_badge
                course.program_badge_icon = program_badge_icon
                course.hero_title = hero_title
                course.hero_subtitle = hero_subtitle
                
                # Update repeatable sections
                course.what_you_will_master = what_you_will_master
                course.who_should_attend = who_should_attend
                course.program_structure = program_structure
                
                # Handle dates
                if start_date:
                    course.start_date = start_date
                if end_date:
                    course.end_date = end_date
                if enrollment_deadline:
                    course.enrollment_deadline = enrollment_deadline
                
                # Handle foreign keys
                if category_id:
                    course.category_id = category_id
                if department_id:
                    course.department_id = department_id
                if instructor_id:
                    course.instructor_id = instructor_id
                    
                course.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'Course "{course_name}" updated successfully!'})
                else:
                    messages.success(request, f'Course "{course_name}" updated successfully!')
                    return redirect('course_management')
                    
            except Course.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Course not found!'})
                else:
                    messages.error(request, 'Course not found!')
                    return redirect('course_management')
                    
        else:  # Add new course
            try:
                # Create new course
                course = Course(
                    course_name=course_name,
                    description=description,
                    credits=credits,
                    duration_weeks=duration_weeks,
                    schedule_type=schedule_type,
                    batch_size=batch_size,
                    course_fee=course_fee,
                    max_students=max_students,
                    certification_provided=certification_provided,
                    certification_name=certification_name,
                    enrollment_open=enrollment_open,
                    program_badge=program_badge,
                    program_badge_icon=program_badge_icon,
                    hero_title=hero_title,
                    hero_subtitle=hero_subtitle,
                    what_you_will_master=what_you_will_master,
                    who_should_attend=who_should_attend,
                    program_structure=program_structure,
                )
                
                # Handle dates
                if start_date:
                    course.start_date = start_date
                if end_date:
                    course.end_date = end_date
                if enrollment_deadline:
                    course.enrollment_deadline = enrollment_deadline
                
                # Handle foreign keys
                if category_id:
                    course.category_id = category_id
                if department_id:
                    course.department_id = department_id
                if instructor_id:
                    course.instructor_id = instructor_id
                    
                course.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': f'Course "{course_name}" created successfully! Course Code: {course.get_short_uuid()}'})
                else:
                    messages.success(request, f'Course "{course_name}" created successfully!')
                    return redirect('course_management')
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'Error creating course: {str(e)}'})
                else:
                    messages.error(request, f'Error creating course: {str(e)}')
                    return redirect('course_management')
    
    # GET request - show all courses with related data
    courses = Course.objects.all().select_related('category', 'department', 'instructor').order_by('-created_at')
    
    # Pass additional data for dropdowns
    categories = CourseCategory.objects.all()
    departments = Department.objects.all()
    instructors = Instructor.objects.all()
    
    context = {
        'courses': courses,
        'categories': categories,
        'departments': departments,
        'instructors': instructors,
    }
    return render(request, 'training_institute_app/dashboard/courses/course-management.html', context)