from django.test import TestCase
from django.contrib.auth.models import User
from courses.models import Course, Category
from .models import Cart, CartItem, Enrollment


class CartModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='تست', slug='test')
        self.course = Course.objects.create(
            title='دوره تست',
            slug='test-course',
            description='...',
            instructor=self.user,
            category=self.category,
            price=100000,
        )

    def test_cart_creation(self):
        cart, created = Cart.objects.get_or_create(user=self.user)
        self.assertFalse(created)
        self.assertEqual(cart.user, self.user)

    def test_cart_item_add(self):
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, course=self.course)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.total_price, 100000)

    def test_enrollment(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        self.assertEqual(self.user.enrollments.count(), 1)