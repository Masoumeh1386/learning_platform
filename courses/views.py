from django.shortcuts import render, get_object_or_404,redirect
from .models import Course, Category,Lesson,Comment,Rating
from django.contrib.auth.decorators import login_required
from orders.models import Enrollment
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import CourseForm, LessonForm, CommentForm, RatingForm
from django.db.models import Sum

def home(request):
    latest_courses = Course.objects.filter(is_published=True).order_by('-created_at')[:6]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'latest_courses': latest_courses,
        'categories': categories,
    })




def course_list(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    level = request.GET.get('level')
    price = request.GET.get('price')
    sort = request.GET.get('sort', '-created_at')

    courses = Course.objects.filter(is_published=True)

    # جستجو
    if query:
        courses = courses.filter(title__icontains=query)

    # فیلتر دسته
    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    # فیلتر سطح
    if level:
        courses = courses.filter(level=level)

    # فیلتر قیمت
    if price == 'free':
        courses = courses.filter(price=0)
    elif price == 'paid':
        courses = courses.filter(price__gt=0)

    # مرتب‌سازی
    if sort == 'cheap':
        courses = courses.order_by('price')
    elif sort == 'expensive':
        courses = courses.order_by('-price')
    elif sort == 'oldest':
        courses = courses.order_by('created_at')
    else:
        courses = courses.order_by('-created_at')

    # صفحه‌بندی
    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'courses/course_list.html', {
        'courses': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'selected_level': level,
        'selected_price': price,
        'selected_sort': sort,
        'query': query,
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    courses = Course.objects.filter(category=category, is_published=True)
    categories = Category.objects.all()
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'categories': categories,
        'selected_category': slug,
    })



def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lessons = course.lessons.all().order_by('order')
    comments = course.comments.all()

    # میانگین امتیاز
    ratings = course.ratings.all()
    avg_rating = 0
    if ratings.exists():
        avg_rating = round(sum(r.score for r in ratings) / ratings.count(), 1)

    is_enrolled = False
    user_rating = None
    if request.user.is_authenticated:
        from orders.models import Enrollment
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        user_rating = Rating.objects.filter(user=request.user, course=course).first()

    # کامنت جدید
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        rating_form = RatingForm(request.POST)

        if 'submit_comment' in request.POST and comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.course = course
            comment.user = request.user
            comment.save()
            messages.success(request, 'کامنت ثبت شد.')
            return redirect('course_detail', slug=course.slug)

        if 'submit_rating' in request.POST and rating_form.is_valid():
            score = rating_form.cleaned_data['score']
            Rating.objects.update_or_create(
                user=request.user, course=course,
                defaults={'score': score}
            )
            messages.success(request, 'امتیاز شما ثبت شد.')
            return redirect('course_detail', slug=course.slug)

    comment_form = CommentForm()
    rating_form = RatingForm(instance=user_rating)

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'comments': comments,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'avg_rating': avg_rating,
        'user_rating': user_rating,
    })


def search(request):
    query = request.GET.get('q')
    courses = Course.objects.filter(is_published=True)

    if query:
        courses = courses.filter(title__icontains=query)

    return render(request, 'courses/search.html', {
        'courses': courses,
        'query': query,
    })




@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).order_by('-enrolled_at')
    return render(request, 'courses/my_courses.html', {
        'enrollments': enrollments,
    })




@login_required
def learning_page(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.warning(request, 'برای دسترسی به درس‌ها باید در دوره ثبت‌نام کنی.')
        return redirect('course_detail', slug=course.slug)

    lessons = course.lessons.all().order_by('order')
    first_lesson = lessons.first()

    return render(request, 'courses/learning_page.html', {
        'course': course,
        'lessons': lessons,
        'first_lesson': first_lesson,
    })


@login_required
def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)

    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.warning(request, 'برای دسترسی به درس‌ها باید در دوره ثبت‌نام کنی.')
        return redirect('course_detail', slug=course.slug)

    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    lessons = course.lessons.all().order_by('order')

    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
    })




@login_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'دوره با موفقیت اضافه شد.')
            return redirect('my_created_courses')
    else:
        form = CourseForm()

    return render(request, 'courses/add_course.html', {'form': form})


@login_required
def my_created_courses(request):
    courses = Course.objects.filter(instructor=request.user).order_by('-created_at')
    return render(request, 'courses/my_created_courses.html', {'courses': courses})


@login_required
def add_lesson(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'درس با موفقیت اضافه شد.')
            return redirect('add_lesson', slug=course.slug)
    else:
        form = LessonForm()

    lessons = course.lessons.all().order_by('order')

    return render(request, 'courses/add_lesson.html', {
        'form': form,
        'course': course,
        'lessons': lessons,
    })


@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'دوره با موفقیت ویرایش شد.')
            return redirect('my_created_courses')
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})


@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'دوره با موفقیت حذف شد.')
        return redirect('my_created_courses')

    return render(request, 'courses/delete_course.html', {'course': course})


@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'درس با موفقیت ویرایش شد.')
            return redirect('add_lesson', slug=lesson.course.slug)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'courses/edit_lesson.html', {'form': form, 'lesson': lesson})


@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)

    if request.method == 'POST':
        course_slug = lesson.course.slug
        lesson.delete()
        messages.success(request, 'درس با موفقیت حذف شد.')
        return redirect('add_lesson', slug=course_slug)

    return render(request, 'courses/delete_lesson.html', {'lesson': lesson})






@login_required
def instructor_stats(request):
    courses = Course.objects.filter(instructor=request.user)

    total_courses = courses.count()
    total_students = 0
    total_revenue = 0

    course_data = []
    for course in courses:
        students_count = course.enrollments.count()
        revenue = students_count * course.price
        total_students += students_count
        total_revenue += revenue

        course_data.append({
            'course': course,
            'students_count': students_count,
            'revenue': revenue,
        })

    return render(request, 'courses/instructor_stats.html', {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_revenue': total_revenue,
        'course_data': course_data,
    })

