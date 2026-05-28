import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    phone_number = models.CharField(max_length=17, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    google_picture = models.URLField(max_length=500, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    user_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)
    is_active_user = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return self.full_name or self.username


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class AboutPage(models.Model):
    """Single model for all about page content"""
    
    # Hero Section
    hero_title_line1 = models.CharField(max_length=200)
    hero_title_line2 = models.CharField(max_length=200)
    hero_subtitle = models.TextField()
    hero_badge_text = models.CharField(max_length=50)
    hero_badge_icon = models.CharField(max_length=50)
    
    # Mission, Vision & Values (JSON)
    mission_vision_items = models.JSONField()
    
    # Timeline Events (JSON)
    timeline_items = models.JSONField()
    
    # Team Members (JSON)
    team_members = models.JSONField()
    
    # Statistics (JSON)
    statistics = models.JSONField()
    
    # Why Choose Us Features (JSON)
    why_us_features = models.JSONField()
    
    # Section visibility toggles
    show_mission_vision = models.BooleanField(default=True)
    show_timeline = models.BooleanField(default=True)
    show_leadership = models.BooleanField(default=True)
    show_stats = models.BooleanField(default=True)
    show_why_us = models.BooleanField(default=True)
    
    # Section headers
    timeline_section_tag = models.CharField(max_length=50)
    timeline_section_title = models.CharField(max_length=200)
    timeline_section_subtitle = models.TextField()
    
    leadership_section_tag = models.CharField(max_length=50)
    leadership_section_title = models.CharField(max_length=200)
    leadership_section_subtitle = models.TextField()
    
    why_us_section_tag = models.CharField(max_length=50)
    why_us_section_title = models.CharField(max_length=200)
    why_us_section_subtitle = models.TextField()
    
    # Active status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"
    
    def __str__(self):
        return "About Page Content"
        

class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class TrainingArea(models.Model):
    """Core training areas like Software Development, Mobile Development, etc."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='fa-solid fa-laptop-code')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='training_areas')
    
    def __str__(self):
        return self.name


class TrainingTopic(models.Model):
    """Individual topics under training areas"""
    name = models.CharField(max_length=200)
    training_area = models.ForeignKey(TrainingArea, on_delete=models.CASCADE, related_name='topics')
    
    def __str__(self):
        return self.name


class CurriculumModule(models.Model):
    """Curriculum modules for the course"""
    MODULE_TYPES = [
        ('FRONTEND', 'Frontend Development'),
        ('BACKEND', 'Backend Development'),
        ('MOBILE', 'Mobile & Cloud'),
        ('SECURITY', 'Security & Best Practices'),
        ('DATABASE', 'Database Design'),
        ('DEVOPS', 'DevOps & Deployment'),
    ]
    
    name = models.CharField(max_length=200)
    module_type = models.CharField(max_length=20, choices=MODULE_TYPES)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='fa-solid fa-code')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='curriculum_modules')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class CurriculumTopic(models.Model):
    """Individual topics under curriculum modules"""
    name = models.CharField(max_length=200)
    module = models.ForeignKey(CurriculumModule, on_delete=models.CASCADE, related_name='topics')
    
    def __str__(self):
        return self.name


class LearningOutcome(models.Model):
    """Learning outcomes for the course"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fa-solid fa-rocket')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='learning_outcomes')
    
    def __str__(self):
        return self.title


class TargetAudience(models.Model):
    """Target audience for the course"""
    audience_type = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, default='fa-solid fa-users')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='target_audiences')
    
    def __str__(self):
        return self.audience_type


class Instructor(models.Model):
    """Course instructor details"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile', null=True, blank=True)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    bio = models.TextField()
    avatar_icon = models.CharField(max_length=50, default='fa-solid fa-user-graduate')
    experience_years = models.IntegerField(default=0)
    students_trained = models.IntegerField(default=0)
    instructor_rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.9)
    email = models.EmailField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Course(models.Model):
    # Basic Information
    course_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Course Details
    duration_weeks = models.IntegerField(default=12)
    schedule_type = models.CharField(max_length=50, default='Flexible', help_text="e.g., Flexible, Evening, Weekend")
    batch_size = models.CharField(max_length=50, default='15-20', help_text="e.g., 15-20, 25-30")
    
    # Rating and Reviews
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.8)
    total_reviews = models.IntegerField(default=0)
    
    # Certification
    certification_provided = models.BooleanField(default=True)
    certification_name = models.CharField(max_length=200, default="Industry Certification", blank=True)
    
    # Categorization
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Financial
    course_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    emi_available = models.BooleanField(default=True)
    scholarship_available = models.BooleanField(default=True)
    
    # Capacity
    max_students = models.IntegerField(default=30)
    current_enrolled = models.IntegerField(default=0)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Instructor
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    
    # Additional Staff
    assistant_instructor = models.CharField(max_length=200, blank=True, null=True)
    support_staff = models.CharField(max_length=200, blank=True, null=True)
    
    # Enrollment Info
    enrollment_open = models.BooleanField(default=True)
    enrollment_deadline = models.DateField(blank=True, null=True)
    
    # Badge/Program Type
    program_badge = models.CharField(max_length=50, default="ICT & SOFTWARE DEVELOPMENT")
    program_badge_icon = models.CharField(max_length=50, default="fa-solid fa-laptop-code")
    
    # Hero Section
    hero_title = models.CharField(max_length=200, blank=True)
    hero_subtitle = models.CharField(max_length=500, blank=True)
    what_you_will_master = models.JSONField(default=list, blank=True)
    who_should_attend = models.JSONField(default=list, blank=True)
    program_structure = models.JSONField(default=list, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.course_name
    
    def get_short_uuid(self):
        """Return first 8 characters of UUID for display"""
        return str(self.course_code).split('-')[0]
    
    def get_average_rating(self):
        """Calculate average rating from reviews"""
        if self.total_reviews > 0:
            return self.rating
        return 4.8
    
    def get_enrollment_percentage(self):
        """Get enrollment percentage"""
        if self.max_students > 0:
            return (self.current_enrolled / self.max_students) * 100
        return 0
    
    def is_full(self):
        """Check if course is full"""
        return self.current_enrolled >= self.max_students
    
    def has_available_seats(self):
        """Check if seats are available"""
        return self.current_enrolled < self.max_students
    
    def get_available_seats(self):
        """Get number of available seats"""
        return self.max_students - self.current_enrolled


class CourseReview(models.Model):
    """Student reviews for courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['course', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.course_name} - {self.rating}★"


class CourseFAQ(models.Model):
    """Frequently asked questions for courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
        ('REFUNDED', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    enrollment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    # Additional enrollment info
    enrollment_number = models.CharField(max_length=50, unique=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrollment_date']
    
    def save(self, *args, **kwargs):
        if not self.enrollment_number:
            self.enrollment_number = f"ENR-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.course_name}"


class CourseLecturer(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lecturers')
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_courses')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.lecturer.username} - {self.course.course_name}"


class ContactInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=17, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    status = models.CharField(max_length=20, default='PENDING')
    response = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"