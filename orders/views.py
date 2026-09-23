from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course
from .models import Enrollment,CartItem,Cart, Order, OrderItem


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'شما قبلاً در این دوره ثبت‌نام کرده‌اید.')
        return redirect('course_detail', slug=course.slug)

    if course.price == 0:
        Enrollment.objects.create(user=request.user, course=course)
        course.students.add(request.user)
        messages.success(request, 'با موفقیت در دوره ثبت‌نام شدید!')
        return redirect('course_detail', slug=course.slug)
    else:
        messages.info(request, 'این دوره پولی است. لطفاً ابتدا آن را خریداری کنید.')
        return redirect('course_detail', slug=course.slug)


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    return render(request, 'orders/cart.html', {
        'cart': cart,
        'items': items,
    })


@login_required
def add_to_cart(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if CartItem.objects.filter(cart=cart, course=course).exists():
        messages.warning(request, 'این دوره قبلاً در سبد شماست.')
    elif Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'شما قبلاً در این دوره ثبت‌نام کرده‌اید.')
    else:
        CartItem.objects.create(cart=cart, course=course)
        messages.success(request, 'دوره به سبد خرید اضافه شد.')

    return redirect('cart_detail')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'دوره از سبد حذف شد.')
    return redirect('cart_detail')


@login_required
def clear_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    messages.success(request, 'سبد خرید خالی شد.')
    return redirect('cart_detail')


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    if not items:
        messages.warning(request, 'سبد خرید شما خالیه.')
        return redirect('course_list')

    total = cart.total_price

    if request.method == 'POST':
        # ساخت سفارش
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            is_paid=True,
        )

        # کپی آیتم‌های سبد توی OrderItem و ثبت‌نام در دوره
        for item in items:
            OrderItem.objects.create(
                order=order,
                course=item.course,
                price=item.course.price,
            )

            Enrollment.objects.get_or_create(
                user=request.user,
                course=item.course,
            )

            item.course.students.add(request.user)

        # خالی کردن سبد
        items.delete()

        messages.success(request, 'خرید با موفقیت انجام شد!')
        return redirect('order_success', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'items': items,
        'total': total,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})