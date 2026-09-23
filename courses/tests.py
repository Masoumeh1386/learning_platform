from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Course, Lesson, Comment, Rating


class CourseModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='برنامه‌نویسی', slug='programming')
        self.course = Course.objects.create(
            title='آموزش پایتون',
            slug='python-course',
            description='توضیحات تست',
            instructor=self.user,
            category=self.category,
            price=500000,
            level='beginner',
        )

    def test_course_creation(self):
        self.assertEqual(self.course.title, 'آموزش پایتون')
        self.assertEqual(self.course.price, 500000)
        self.assertTrue(self.course.is_published)

    def test_course_str(self):
        self.assertEqual(str(self.course), 'آموزش پایتون')

    def test_course_instructor(self):
        self.assertEqual(self.course.instructor.username, 'testuser')

    def test_average_rating_with_no_ratings(self):
        self.assertEqual(self.course.average_rating, 0)

    def test_average_rating_with_ratings(self):
        user2 = User.objects.create_user(username='user2', password='12345')
        Rating.objects.create(course=self.course, user=self.user, score=5)
        Rating.objects.create(course=self.course, user=user2, score=3)
        self.assertEqual(self.course.average_rating, 4.0)


class CourseViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='برنامه‌نویسی', slug='programming')
        self.course = Course.objects.create(
            title='آموزش پایتون',
            slug='python-course',
            description='توضیحات',
            instructor=self.user,
            category=self.category,
            price=0,
            is_published=True,
        )

    def test_course_list_view(self):
        response = self.client.get('/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'آموزش پایتون')

    def test_course_detail_view(self):
        response = self.client.get(f'/courses/course/{self.course.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'آموزش پایتون')

    def test_course_detail_404(self):
        response = self.client.get('/courses/course/not-exist/')
        self.assertEqual(response.status_code, 404)

    def test_search_view(self):
        response = self.client.get('/courses/?q=پایتون')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'آموزش پایتون')

