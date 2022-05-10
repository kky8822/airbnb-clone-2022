import os
from pickletools import read_uint1
import requests
from django.views import View
from django.views.generic import FormView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.contrib import messages

from . import forms, models


class LoginView(FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


def log_out(request):
    messages.info(request, f"Bye {request.user.first_name}, see you soon")
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    # initial = {
    #     "first_name": "Kyeyeop",
    #     "last_name": "Kim",
    #     "email": "kky8822@gmail.com",
    # }

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # to do: success message
    except models.User.DoesNotExist:
        # to do: add error message
        pass

    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://localhost:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user,user:email"
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        code = request.GET.get("code", None)
        if code is not None:
            result = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            result_json = result.json()
            error = result_json.get("error", None)
            if error is not None:
                raise GithubException("Can not get Github token")
            else:
                access_token = result_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                email_request = requests.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                email_json = email_request.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    email = email_json[0].get("email")
                    bio = profile_json.get("bio")
                    avatar_url = profile_json.get("avatar_url")

                    if bio is None:
                        bio = ""
                    try:
                        user = models.User.objects.get(email=email)
                        admin = models.User.objects.get(
                            email=os.environ.get("ADMIN_EMAIL")
                        )
                        if user.login_method != models.User.LOGIN_GITHUB:
                            if user == admin:
                                login(request, user)
                                return redirect(reverse("core:home"))
                            else:
                                raise GithubException(
                                    f"please log in with {user.login_method}"
                                )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            email_verified=True,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                        )
                        user.set_unusable_password()
                        user.save()
                        if avatar_url is not None:
                            photo_request = requests.get(avatar_url)
                            user.avatar.save(
                                f"{name}-avatar", ContentFile(photo_request.content)
                            )
                    login(request, user)
                    messages.success(request, f"Welcome Back {user.first_name}")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can not get user information from Gihub API")
        else:
            raise GithubException("Can not get Github code")
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    REST_API_KEY = os.environ.get("KAKAO_ID")
    REDIRECT_URI = "http://localhost:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        # raise KakaoException("Test Kakao auth error")
        code = request.GET.get("code")
        REST_API_KEY = os.environ.get("KAKAO_ID")
        REDIRECT_URI = "http://localhost:8000/users/login/kakao/callback"
        token_request = requests.post(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Can not get Kakao token")
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com//v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email", None)
        profile = kakao_account.get("profile")
        nickname = profile.get("nickname", None)
        avatar_url = profile.get("profile_image_url", None)
        if email is None:
            raise KakaoException("Can not get user information from Kakao API")
        try:
            user = models.User.objects.get(email=email)
            admin = models.User.objects.get(email=os.environ.get("ADMIN_EMAIL"))
            if user.login_method != models.User.LOGIN_KAKAO:
                if user == admin:
                    login(request, user)
                    return redirect(reverse("core:home"))
                else:
                    raise KakaoException(f"Please log in with {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                email_verified=True,
                first_name=nickname,
                username=email,
                login_method=models.User.LOGIN_KAKAO,
            )
            user.set_unusable_password()
            user.save()
            if avatar_url is not None:
                photo_request = requests.get(avatar_url)
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(photo_request.content)
                )

        login(request, user)
        messages.success(request, f"Welcome Back {user.first_name}")
        return redirect(reverse("core:home"))
    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):
    model = models.User
    context_object_name = "user_obj"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["hello"] = "Hello!"
    #     return context
