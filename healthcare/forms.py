from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    # We add a choice field to the standard User form
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            role = self.cleaned_data.get('role')
            
            # If the user is a doctor, create the empty Doctor profile
            if role == 'doctor':
                from .models import Doctor
                Doctor.objects.create(
                    user=user, 
                    specialty="General Physician" # Default value
                )
        return user
       