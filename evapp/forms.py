from django import forms
from .models import Users
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
import re

class SignUp(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'userpw2', 'placeholder': '비밀번호 확인'}))

    class Meta:
        model = Users
        fields = ['userid', 'password', 'name', 'email']
        widgets = {
            'userid': forms.TextInput(attrs={'class': 'userid', 'placeholder': '아이디'}),
            'password': forms.PasswordInput(attrs={'class': 'userpw', 'placeholder': '비밀번호'}),
            'name': forms.TextInput(attrs={'class': 'name', 'placeholder': '이름'}),
            'email': forms.EmailInput(attrs={'class': 'email', 'placeholder': '이메일'}),
        }

    # 비밀번호 확인 로직
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password:
            if len(password) < 8:
                raise ValidationError("비밀번호는 최소 8자리 이상이어야 합니다.")

        if password and password2 and password != password2:
            raise ValidationError("비밀번호가 일치하지 않습니다.")

        return password2

    # 이메일 중복 확인
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if re.search(r'[가-힣]', email):
            raise ValidationError("이메일에 한글을 포함할 수 없습니다.")

        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, email):
            raise ValidationError("유효한 이메일 주소를 입력해주세요.")

        if Users.objects.filter(email=email).exists():
            raise ValidationError("중복된 이메일 입니다.")
        return email

    # 아이디 중복 확인 및 커스텀 메시지
    def clean_userid(self):
        userid = self.cleaned_data.get('userid')

        # 한글 포함 여부 확인
        if re.search(r'[가-힣]', userid):
            raise ValidationError("아이디에 한글을 포함할 수 없습니다.")

        # 아이디 중복 확인
        if Users.objects.filter(userid=userid).exists():
            raise ValidationError(mark_safe(f"'{userid}'아이디는 이미 사용 중입니다. 다른 아이디를 입력해주세요."))

        return userid