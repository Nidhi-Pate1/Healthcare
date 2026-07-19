from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.FloatField()
    description = models.TextField()
    
    # Replaced local ImageField with a web URL string safe for free servers (like Render)
    # Includes a clean placeholder fallback if no link is provided
    image_url = models.URLField(
        max_length=1000, 
        blank=True, 
        null=True, 
        default="https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500"
    )

    def __str__(self):
        return self.name
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'medicine') 

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicines = models.ManyToManyField(Medicine)
    total_price = models.FloatField()
    status = models.CharField(max_length=100, default="Pending")


class Doctor(models.Model):
    # Link this profile to a specific User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    
    # Doctor specific fields
    specialty = models.CharField(max_length=100)
    experience = models.IntegerField(default=0)
    clinic_address = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00) # Add this!
    
    # Consultancy options
    video_consultancy = models.BooleanField(default=True)
    clinic_visit = models.BooleanField(default=True)
    home_visit = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr. {self.user.last_name} ({self.specialty})"
# healthcare/models.py
from django.db import models
from django.contrib.auth.models import User

# ... your Doctor model is here ...

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    appointment_type = models.CharField(max_length=50) # e.g., Video, Clinic, Home
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.user.last_name} on {self.date}"
    # healthcare/models.py
from django.db import models
from django.contrib.auth.models import User

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Remove the 'placeholder' argument
    medical_history = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class MedicalReport(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='patient_reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
        

class DoctorConsultation(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor_name = models.CharField(max_length=100)
    appointment_date = models.DateTimeField()
    meeting_link = models.URLField()
    meeting_link = models.URLField(blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)

def __str__(self):
        return f"{self.patient.username} - {self.doctor_name}"

class Appointment(models.Model):
    patient = models.ForeignKey(User,on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)

    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(
        max_length=20,
        default='pending'
    )

    mode = models.CharField(
        max_length=20,
        default='chat'
    )

    message = models.TextField(
        blank=True,
        null=True
    )

    meeting_link = models.URLField(
        blank=True,
        null=True
    )