from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager — email se user create karta hai, username se nahi
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email zaroori hai!')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model — Teen roles: PATIENT, DOCTOR, ADMIN
    """

    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    ]

    # Basic Fields
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True, null=True)

    # Role Field — sabse important!
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='PATIENT'
    )

    # Account Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Email se login hoga, username se nahi
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class DoctorProfile(models.Model):
    """
    Doctor ka extra profile — sirf DOCTOR role wale users ka hoga
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialty = models.CharField(max_length=100)
    experience_years = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )
    rating = models.FloatField(default=0.0)
    location = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)

    # Availability
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'doctor_profiles'

    def __str__(self):
        return f"Dr. {self.user.full_name} — {self.specialty}"
