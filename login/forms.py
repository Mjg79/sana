from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm



class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].initial = ""
        self.fields.keyOrder = [
            'username', 'password'
        ]
    
    def clean(self):
        cd = super(LoginForm, self).clean()
        password = cd.get('password')
        username = cd.get('username')
        try:
            username = username.lower()
        except AttributeError:
            pass
        if username:
            try:
                m = User.objects.get(username=username)
                if not m.check_password(password):
                    self.errors['password'] = u'Incorrect username or password.'
                    return
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                self.errors['password'] = u'Incorrect username or password.'
                return
            user = authenticate(username=m.username, password=password)
            if user is not None:
                if not user.is_active:
                    self.errors['username'] = u"Your account is not activate."
                    return
                self.user = user
            else:
                self.errors['password'] = u'Incorrect username or password.'
                return

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )
    
    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user