from django.test import TestCase
from .models import Category

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        root = Category.objects.create(name='Root', slug='root')
        child = Category.objects.create(name='Child', slug='child', parent=root)
        
        self.assertEqual(root.name, 'Root')
        self.assertEqual(child.parent, root)
        self.assertIn(child, root.get_children())