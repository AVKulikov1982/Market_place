import re
from django.shortcuts import render
from app_users.models import Profile, Image
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def account_view(request):
    profile = Profile.objects.filter(user_id=request.user.id).get()
    avatar_object = Image.objects.filter(profile_id=profile)
    data = {
        "full_name": profile.fullname,
        "avatar": avatar_object[0].avatar
    }
    return render(request, "account.html", context=data)


def validate_fullname(prev, curr):
    if prev == curr:
        return True, None, prev
    else:
        if len(re.findall(r'\w+', curr)) == 3:
            return True, None, curr
        else:
            return False, "Введите ФИО в соответствии с шаблоном Фамилия Имя Отчество", curr


def validate_phone(prev, curr):
    if prev == curr:
        return True, None, prev
    elif Profile.objects.filter(phone_number=curr).exists() and prev != curr:
        return False, "Пользователь с данным номером телефона уже существует", curr
    elif re.match(r'(\+7|8).*?(\d{3}).*?(\d{3}).*?(\d{2}).*?(\d{2})', curr) and len(curr) == 12:
        return True, None, curr
    else:
        return False, "Введите номер телефона в соответствии с шаблоном +70000000000", curr


def validate_email(prev, curr):
    if prev == curr:
        return True, None, prev
    elif User.objects.filter(email=curr).exists() and prev != curr:
        return False, "Пользователь с таким email уже существует", curr
    elif re.match(r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$", curr):
        return True, None, curr
    else:
        return False, "Введите email в соответствии с шаблоном me@host.com", curr


def validate_passwords(password, password_reply):
    if re.match(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z]{8,}$', password) and password == password_reply:
        return True, None, True, None
    elif not re.match(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z]{8,}$', password):
        return False, "Пароль должен состоять по крайней мере из восьми символов, содержат символы в верхнем и нижнем регистрах и включать по крайней мере одну цифру", True, None
    else:
        return True, None, False, "Пароли не совпадают"


class EditProfile(View):
    def get(self, request):
        profile = Profile.objects.filter(user_id=request.user.id).get()
        data = {
            "avatar_changed": False,
            "avatar_correct": True,
            "avatar_error": None,

            "name_correct": True,
            "name_error": None,
            "name": profile.fullname,

            "phone_correct": True,
            "phone_error": None,
            "phone": profile.phone_number,

            "email_correct": True,
            "email_error": None,
            "email": request.user.email,

            "password_correct": True,
            "password_error": None,

            "password_reply_correct": True,
            "password_reply_error": None,

            "changed_successfully": False
        }
        return render(request, "profile.html", context=data)

    def post(self, request):
        # TODO: добавить изменение аватарки + валидация
        # TODO: добавить border color в случае ошибки в profile.html

        profile = Profile.objects.filter(user_id=request.user.id).get()

        data = {
            "avatar_changed": False,
            "avatar_correct": True,
            "avatar_error": None,
        }

        new_name = request.POST.get("name")
        data["name_correct"], data["name_error"], data["name"] = validate_fullname(profile.fullname, new_name)
        if data["name_correct"]:
            profile.fullname = new_name
            profile.save()

        new_phone = request.POST.get("phone")
        data["phone_correct"], data["phone_error"], data["phone"] = validate_phone(profile.phone_number, new_phone)
        if data["phone_correct"]:
            profile.phone_number = new_phone
            profile.save()

        new_email = request.POST.get("mail")
        data["email_correct"], data["email_error"], data["email"] = validate_email(request.user.email, new_email)
        if data["email_correct"]:
            user = User.objects.get(id=request.user.id)
            user.email = new_email
            user.save()

        new_password = request.POST.get("password")
        new_password_reply = request.POST.get("passwordReply")
        if new_password != "":
            data["password_correct"], data["password_error"], data["password_reply_correct"], data["password_reply_error"] = validate_passwords(new_password, new_password_reply)
            if data["password_correct"] and data["password_reply_correct"]:
                user = User.objects.get(id=request.user.id)
                user.set_password(new_password)
                user.save()
                user = authenticate(username=user.username, password=new_password)
                login(request, user)
        else:
            data["password_correct"], data["password_error"], data["password_reply_correct"], data["password_reply_error"] = True, None, True, None

        if data["avatar_correct"] and data["name_correct"] and data["phone_correct"] and data["email_correct"] and data["password_correct"] and data["password_reply_correct"]:
            data["changed_successfully"] = True
        else:
            data["changed_successfully"] = False

        return render(request, "profile.html", context=data)
