# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from django import forms
from django.contrib.auth.models import User
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput


class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label=u"用户名",
        error_messages={'required': '请输入用户名'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"用户名",
            }
        ),
    )
    password = forms.CharField(
        required=True,
        label=u"密码",
        error_messages={'required': u'请输入密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"密码",
            }
        ),
    )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"用户名和密码为必填项")
        else:
            cleaned_data = super(LoginForm, self).clean()
"""

class LoginForm(forms.Form):
    username = forms.CharField(error_messages={'required':'请输入用户名'})
    password = forms.CharField(widget=forms.PasswordInput,error_messages={'required':'请输入密码'})

    def clean(self):
        cleaned_data=super(LoginForm,self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            try:
                member=Register.objects.get(username__exact=username)
            except Register.DoesNotExist:
                self._errors['username'] = self.error_class([u"用户不存在"])
                return
            if member.password != password:
                self._errors['password'] = self.error_class([u"密码不一致"])
        return cleaned_data
"""