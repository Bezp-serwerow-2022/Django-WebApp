from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
import structlog
logger = structlog.get_logger('base')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            logger.info('Creating user', action='create_user', email=user.email)
            username = form.cleaned_data.get('username')
            user.is_active=True
            user.save()
            messages.success(request, f'Your account has been created! You are now able to log in')
            logger.info('User created', action='create_user', email=user.email)
            return redirect('login')
        else:
            return render(request, 'users/register.html', {'form': form})
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        logger.info('Editing user', action='edit_user', user=request.user.pk)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if (u_form.is_valid() and p_form.is_valid()):
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            logger.info('User updated', action='edit_user', user=request.user.pk)
            return redirect('profile')
        else:
            return render(request, 'users/profile.html', {'form': form})

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)
