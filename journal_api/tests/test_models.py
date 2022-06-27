from django.test import TestCase

from journal_api.models import Category


class ModelTests(TestCase):
    def test_category_autoincrement(self):
        category = Category.objects.create(name="testcategory")
        category_2 = Category.objects.create(name="testcategory2")
        self.assertEqual(category.id, 1)
        self.assertEqual(category_2.id, 2)
