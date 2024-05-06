from datetime import datetime

from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from .forms import RegisterUserForm, LoginUserForm, ProfileForm, UserForm
from .models import Profile, User
from reservations.models import BookingModel


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('profile')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('hotels')


def logout_user(request):
    logout(request)
    return redirect('login')


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        current_date = datetime.now().date()
        user = get_object_or_404(User, pk=request.user.id)
        profile_form = ProfileForm()
        user_form = UserForm()
        bookings = BookingModel.objects.filter(user_id=user.id).order_by('-check_out_date')
        future_bookings = bookings.filter(check_in_date__gt=current_date, deleted=False)
        current_bookings = bookings.filter(check_in_date__lte=current_date, check_out_date__gte=current_date,
                                           deleted=False)
        booking_history = bookings.filter(check_out_date__lt=current_date, deleted=False)
        canceled_bookings = bookings.filter(deleted=True)
        return render(request, 'users/profile.html',
                      context={'user': user, 'user_form': user_form, 'profile_form': profile_form,
                               'future_bookings': future_bookings, 'booking_history': booking_history,
                               'current_bookings': current_bookings, 'canceled_bookings': canceled_bookings})

    @transaction.atomic
    def post(self, request):
        no_birth_date = Profile.objects.filter(user=request.user, birth_date=None)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid() and no_birth_date:
            user_form.save()
            profile_form.save()
        return redirect('profile')
