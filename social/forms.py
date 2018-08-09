from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """Extend the User Creation Form to add field"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True )
    email = forms.EmailField(max_length=254, required=True )

    def __init__(self, *args, **kwargs):
        """Override init and add boostrap style to all fields"""
        super(SignUpForm, self).__init__(*args, **kwargs)
        # remove default label suffix of :
        self.label_suffix = ""
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':"form-control",
            'placeholder' : self.fields[field].label })

    class Meta:
        """Add fields to the internal User model/form"""
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
