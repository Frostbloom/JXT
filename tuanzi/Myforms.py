from django import forms

from django.forms import widgets

from tuanzi.models import UserInfo
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

class UserForm(forms.Form):

    user=forms.CharField(max_length=32,
                         error_messages={"required":"该字段不能为空"},
                         label="用户名",
                         widget=widgets.TextInput(attrs={"class":"form-control"},)
                         )
    pwd=forms.CharField(max_length=32,
                         label="密码",
                         widget=widgets.PasswordInput(attrs={"class":"form-control"},)
                        )
    re_pwd=forms.CharField(max_length=32,
                            label="确认密码",
                            widget=widgets.PasswordInput(attrs={"class":"form-control"},)
                           )
    email=forms.EmailField(max_length=32,
                            label="邮箱",
                            widget=widgets.EmailInput(attrs={"class":"form-control"},)
                            )


    def clean_user(self):
        val=self.cleaned_data.get("user")

        user=UserInfo.objects.filter(username=val).first()
        if not user:
            return val
        else:
            raise ValidationError("该用户已注册!")


    def clean(self):
        pwd=self.cleaned_data.get("pwd")
        re_pwd=self.cleaned_data.get("re_pwd")

        if pwd and re_pwd:
            if pwd==re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError("两次密码不一致!")
        else:
            return self.cleaned_data


# 修改密码的表单
class ChangePasswordForm(forms.Form):
	# 三个字段：旧密码、新密码、再输一遍密码
    old_password = forms.CharField(
        label='旧的密码', 
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请输入旧的密码'})
    )
    new_password = forms.CharField(
        label='新的密码', 
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请输入新的密码'})
    )
    new_password_again = forms.CharField(
        label='请再次输入新的密码', 
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请再次输入新的密码'})
    )

    def __init__(self, *args, **kwargs):	
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    
    def clean(self):
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        
        if new_password and new_password_again:
            if new_password == new_password_again:
                return self.cleaned_data
            else:
                raise ValidationError('两次输入的密码不一致')
        else:
            return self.cleaned_data

	# 验证旧的密码是正确的	
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise ValidationError('旧的密码错误')
        return old_password



class AvatarForm(forms.Form):
    
    def __init__(self, *args, **kwargs):	
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(AvatarForm, self).__init__(*args, **kwargs)
    
    
    def clean_user(self):
        val=self.cleaned_data.get("user")

        user=UserInfo.objects.filter(username=val).first()
        if not user:
            return val
        else:
            raise ValidationError("您不是该用户!")



