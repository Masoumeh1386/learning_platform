from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm
from orders.models import Order, Enrollment


@login_required
def profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل با موفقیت ویرایش شد.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
    })


@login_required
def dashboard(request):
    total_orders = Order.objects.filter(user=request.user).count()
    total_enrollments = Enrollment.objects.filter(user=request.user).count()
    total_courses_created = request.user.courses.count()

    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_enrollments = Enrollment.objects.filter(user=request.user).order_by('-enrolled_at')[:5]

    return render(request, 'accounts/dashboard.html', {
        'total_orders': total_orders,
        'total_enrollments': total_enrollments,
        'total_courses_created': total_courses_created,
        'recent_orders': recent_orders,
        'recent_enrollments': recent_enrollments,
    })
