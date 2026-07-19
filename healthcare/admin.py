from django.contrib import admin
from .models import Category, Medicine, Cart, Order, Doctor, Appointment, PatientProfile, MedicalReport,DoctorConsultation

admin.site.register(Category)
admin.site.register(Medicine)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(PatientProfile)
admin.site.register(MedicalReport)
admin.site.register(DoctorConsultation)