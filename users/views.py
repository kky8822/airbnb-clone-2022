import os
from config import settings
from django.http import HttpResponse
import requests
from django.views import View
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils import translation
from . import forms, models, mixins
from reviews import forms as review_form
from conversations import models as conv_models


class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg == None:
            return reverse("core:home")
        else:
            return next_arg


def log_out(request):
    messages.info(request, f"Bye {request.user.first_name}, see you soon")
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(mixins.LoggedOutOnlyView, FormView):
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
            # raise GithubException("Can not get Github code")
            raise GithubException(f"{settings.DATABASES.default}")
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


class UserProfileView(mixins.LoggedInOnlyView, DetailView):
    model = models.User
    context_object_name = "user_obj"
    form_class = review_form.CreateReviewForm

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["hello"] = "Hello!"
    #     return context

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context["form"] = self.form_class
        return context


class UpdateProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    # class Meta:
    model = models.User
    fields = (
        # "email",
        "first_name",
        "last_name",
        # "avatar",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )

    template_name = "users/update-profile.html"
    success_message = "Success upadate profile"

    def get_object(self, queryset=None):
        return self.request.user

    ## email 수정시, username도 email로 copy하여 저장
    # def form_valid(self, form):
    #     email = form.cleaned_data.get("email")
    #     self.object.username = email
    #     self.object.save()
    #     return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["first_name"].widget.attrs = {"placeholder": "First Name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last Name"}
        form.fields["gender"].widget.attrs = {"placeholder": "Gender"}
        form.fields["bio"].widget.attrs = {"placeholder": "Biography"}
        form.fields["birthdate"].widget.attrs = {"placeholder": "Birth Date"}
        form.fields["language"].widget.attrs = {"placeholder": "Language"}
        form.fields["currency"].widget.attrs = {"placeholder": "Currency"}
        return form


class UpdatePasswordView(
    mixins.LoggedInOnlyView,
    mixins.EmailLogintOnlyView,
    SuccessMessageMixin,
    PasswordChangeView,
):

    template_name = "users/update-password.html"
    success_message = "Success upadate password"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        print(form)

        form.fields["old_password"].widget.attrs = {"placeholder": "Current password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Confirm new password"
        }

        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()


@login_required
def switch_hosting(request):
    # request.session.pop("is_hosting", True)
    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True
    return redirect(reverse("core:home"))


def switch_language(request):
    lang = request.GET.get("lang", None)
    response = HttpResponse(200)
    if lang is not None:
        # translation.activate(lang)
        # response = HttpResponse(200)
        # response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return response


class ConversationListView(mixins.LoggedInOnlyView, View):
    def get(self, *args, **kwargs):
        user = self.request.user
        conversations = conv_models.Conversation.objects.filter(participants=user)

        return render(
            self.request,
            "conversations/conversation_list.html",
            {"conversations": conversations},
        )
