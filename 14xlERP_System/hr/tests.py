from django.test import TestCase
from django.contrib.auth.models import User
from .models import Department, Employee, Position


class DepartmentTestCase(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            name='IT'
        )

    def test_department_creation(self):
        self.assertTrue(isinstance(self.dept, Department))
        self.assertEqual(self.dept.name, 'IT')


class PositionTestCase(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='IT')
        self.position = Position.objects.create(
            name='Software Developer',
            department=self.dept
        )

    def test_position_creation(self):
        self.assertTrue(isinstance(self.position, Position))
        self.assertEqual(self.position.name, 'Software Developer')
