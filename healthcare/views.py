import json
import random
import datetime
import io
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django import template
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Unified, single-line models import to prevent double-registration crashes
from .models import Medicine, Cart, Doctor, Appointment, Category, PatientProfile, MedicalReport
from .forms import RegistrationForm

def home_view(request):
    # Fetch medicines for the pharmacy section
    medicines = Medicine.objects.exclude(name="Doctor Consultation Fee")
    context = {'medicines': medicines}

    # Safety check: if Django missed loading the user property, default them gracefully
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        context['role'] = 'patient'
        context['pending_count'] = 0
        return render(request, 'home.html', context)

    # If the user property exists, process their specialized roles normally
    try:
        doctor_profile = Doctor.objects.get(user=request.user)
        context['role'] = 'doctor'
        context['doctor_profile'] = doctor_profile
        context['pending_count'] = Appointment.objects.filter(
            doctor=doctor_profile, 
            status='pending'
        ).count()
    except Doctor.DoesNotExist:
        context['role'] = 'patient'
        context['pending_count'] = 0
    
    return render(request, 'home.html', context)
# 🔐 SIGNUP
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'User already exists'})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')


# 🔐 LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# 🔓 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# 🛒 ADD TO CART (FIXED)
@login_required
def add_to_cart(request, med_id):
    medicine = Medicine.objects.get(id=med_id)

    cart_items = Cart.objects.filter(user=request.user, medicine=medicine)

    if cart_items.exists():
        cart_item = cart_items.first()
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(user=request.user, medicine=medicine, quantity=1)

    return redirect('cart')


# 🛒 VIEW CART
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.medicine.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# ➕ INCREASE QTY
@login_required
def increase_qty(request, item_id):
    item = Cart.objects.get(id=item_id)
    item.quantity += 1
    item.save()
    return redirect('cart')


# ➖ DECREASE QTY
@login_required
def decrease_qty(request, item_id):
    item = Cart.objects.get(id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')


# ❌ REMOVE ITEM
@login_required
def remove_item(request, item_id):
    Cart.objects.get(id=item_id).delete()
    return redirect('cart')

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Cart
import razorpay

@login_required
def payment(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = sum(item.medicine.price * item.quantity for item in cart_items)

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    payment_order = client.order.create({
        "amount": int(total * 100),  # paise
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
    "total": total,
    "order_id": payment_order["id"],
    "razorpay_key": settings.RAZORPAY_KEY_ID,
}
    return render(request, "payment.html", context)



# ✅ PAYMENT SUCCESS
@login_required
def payment_success(request):
    # 1. Logic for the Medicine Shop (Your friend's part)
    Cart.objects.filter(user=request.user).delete()
    
    # 2. Logic for the Doctor Appointment (Your part)
    # We grab the most recent appointment for this user that is still 'unpaid'
    # (Assuming you add a field or use session to track it)
    appointment_id = request.session.get('pending_appt_id')
    
    if appointment_id:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = 'pending' # This makes it visible to the doctor
        appointment.save()
        
        # Clear the session so it doesn't trigger again
        del request.session['pending_appt_id']
        
        # Return the "Strong Visual" success page we made earlier
        return render(request, 'booking_success.html', {'doctor': appointment.doctor})

    # Default fallback to a general success page
    return render(request, 'payment_success.html')

# 📦 ORDERS PAGE
@login_required
def orders(request):
    return render(request, 'orders.html')
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import login

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Automatically log them in after signup
            
            # Redirect based on role
            role = form.cleaned_data.get('role')
            if role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('doctor_list') # Redirect patient to see doctors
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

# healthcare/views.py

from django.contrib.auth.decorators import login_required

@login_required
def doctor_dashboard(request):
   # This finds the doctor profile linked to whoever is logged in
    try:
        doctor = request.user.doctor_profile # Use the related_name we set in models.py
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-date')
        return render(request, 'doctors/dashboard.html', {
            'appointments': appointments,
            'doctor': doctor
        })
    except Doctor.DoesNotExist:
        # If a patient accidentally visits this URL, send them away
        return redirect('doctor_list')
    
def doctor_list(request):
    # Fetch all doctors from the database
    doctors = Doctor.objects.all()
    return render(request, 'doctors/list.html', {'doctors': doctors})
from django.shortcuts import render, get_object_or_404, redirect




@login_required
def book_appointment(request, doctor_id):

    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":

        date = request.POST.get("date")
        time = request.POST.get("time")
        mode = request.POST.get("mode")
        message = request.POST.get("message")

        meeting_link = ""

        if mode == "video":
            room = f"healthcare-{random.randint(1000,9999)}"
            meeting_link = f"https://meet.jit.si/{room}"

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=date,
            time=time,
            mode=mode,
            message=message,
            meeting_link=meeting_link
        )

        service_category, _ = Category.objects.get_or_create(
            name="Services"
        )

        virtual_med, created = Medicine.objects.get_or_create(
            name="Doctor Consultation Fee",
            defaults={
                'price': doctor.consultation_fee,
                'category': service_category,
                'description': 'Consultation Service'
            }
        )

        virtual_med.price = doctor.consultation_fee
        virtual_med.save()

        Cart.objects.get_or_create(
            user=request.user,
            medicine=virtual_med
        )

        request.session['pending_appt_id'] = appointment.id

        return redirect('cart')

    return render(
        request,
        'doctors/book_form.html',
        {
            'doctor': doctor
        }
    )


def update_appointment(request, appt_id, status):
    # This function handles the Accept/Reject buttons
    from .models import Appointment
    appointment = get_object_or_404(Appointment, id=appt_id)
    
    if status == 'confirmed':
        appointment.status = 'confirmed'
    elif status == 'cancelled':
        appointment.status = 'cancelled'
        
    appointment.save()
    return redirect('doctor_dashboard')

    return redirect('patient_dashboard')
@login_required
def patient_dashboard(request):
    # Fetch appointments where the current user is the patient
    # We use '-date' to show the newest ones at the top
    my_appointments = Appointment.objects.filter(patient=request.user).order_by('-date')
    
    return render(request, 'patients/dashboard.html', {
        'appointments': my_appointments
    })
@login_required
def patient_profile(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    reports = MedicalReport.objects.filter(patient=request.user)
    
    if request.method == 'POST':
        if 'update_history' in request.POST:
            profile.medical_history = request.POST.get('history')
            profile.save()
            # We removed the notification line from here
            
        elif 'upload_report' in request.POST:
            file = request.FILES.get('report_file')
            title = request.POST.get('report_title')
            if file and title:
                MedicalReport.objects.create(patient=request.user, title=title, file=file)
            
    return render(request, 'patients/profile.html', {
        'profile': profile,
        'reports': reports
    })

@login_required
def doctor_view_patient(request, appointment_id):
    # 1. Verify this doctor is the one assigned to the appointment (Security check)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    
    # 2. Get the patient from that appointment
    patient_user = appointment.patient
    
    # 3. Fetch their profile and reports
    profile, created = PatientProfile.objects.get_or_create(user=patient_user)
    reports = MedicalReport.objects.filter(patient=patient_user)

    # 4. Render using the 'patients' folder name you prefer
    return render(request, 'patients/patient_detail.html', {
        'patient': patient_user,
        'profile': profile,
        'reports': reports,
        'appointment': appointment
    })
# ---------- AI CHAT ----------
import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful healthcare assistant. Give safe, general medical advice. Do not give prescriptions."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )

            result = response.json()

            reply = result["choices"][0]["message"]["content"]

            return JsonResponse({"response": reply})

        except Exception as e:
            return JsonResponse({"response": "Error: " + str(e)})

    return JsonResponse({"error": "Invalid request"})
    from django.conf import settings
import razorpay
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import DoctorConsultation

@login_required
def consultation(request):

    consultations = DoctorConsultation.objects.filter(
        patient=request.user
    )

    return render(
        request,
        "consultation.html",
        {"consultations": consultations}
    )
    from django.shortcuts import render

def bmi_calculator(request):
    bmi = None
    category = None

    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height')) / 100

        bmi = round(weight / (height ** 2), 2)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

    return render(request, 'bmi_calculator.html',
                  {'bmi': bmi, 'category': category})


def calorie_calculator(request):
    calories = None

    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')

        if gender == 'male':
            calories = round(
                10 * weight + 6.25 * height - 5 * age + 5
            )
        else:
            calories = round(
                10 * weight + 6.25 * height - 5 * age - 161
            )

    return render(request,
                  'calorie_calculator.html',
                  {'calories': calories})