from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home_view, name='home'),

 #  path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('add-to-cart/<int:med_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),

path('payment/', views.payment, name='payment'),

    path('payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
path('increase/<int:item_id>/', views.increase_qty, name='increase'),
path('decrease/<int:item_id>/', views.decrease_qty, name='decrease'),
path('remove/<int:item_id>/', views.remove_item, name='remove'),
    path('orders/', views.orders, name='orders'),
    path('register/', views.register_view, name='register'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
path('update-appointment/<int:appt_id>/<str:status>/', views.update_appointment, name='update_appointment'),
path('my-appointments/', views.patient_dashboard, name='patient_dashboard'),
path('profile/', views.patient_profile, name='patient_profile'),
path('doctor/patient-detail/<int:appointment_id>/', views.doctor_view_patient, name='doctor_view_patient'),
path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
  # ✅ Chatbot route
    path('chatbot/', views.chatbot, name='chatbot'),
    path(
    'consultation/',
    views.consultation,
    name='consultation'
),
    path('bmi-calculator/', views.bmi_calculator, name='bmi_calculator'),
    path('calorie-calculator/', views.calorie_calculator, name='calorie_calculator'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)