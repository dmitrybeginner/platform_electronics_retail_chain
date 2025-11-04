from django.test import TestCase
from django.core.exceptions import ValidationError
from network.models import NetworkNode, Product
from users.models import Employee


class ProductModelTest(TestCase):

    def test_product_creation(self):
        """Test that a Product can be created."""
        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            release_date="2024-01-01"
        )
        self.assertIsInstance(product, Product)
        self.assertEqual(str(product), "Test Product Test Model")


class EmployeeModelTest(TestCase):

    def test_create_employee(self):
        """Test creating a regular employee."""
        user = Employee.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.assertIsInstance(user, Employee)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(str(user), 'testuser')

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = Employee.objects.create_superuser(
            username='super',
            password='password123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class NetworkNodeModelTest(TestCase):

    def setUp(self):
        self.factory = NetworkNode.objects.create(name='Завод')
        self.retail_network = NetworkNode.objects.create(name='Розничная сеть', supplier=self.factory)
        self.entrepreneur = NetworkNode.objects.create(name='ИП', supplier=self.retail_network)

    def test_hierarchy_level_property(self):
        """Test the hierarchy_level property is calculated correctly."""
        self.assertEqual(self.factory.hierarchy_level, 0)
        self.assertEqual(self.retail_network.hierarchy_level, 1)
        self.assertEqual(self.entrepreneur.hierarchy_level, 2)

    def test_node_type_property(self):
        """Test the node_type property returns the correct string."""
        self.assertEqual(self.factory.node_type, 'Завод')
        self.assertEqual(self.retail_network.node_type, 'Розничная сеть')
        self.assertEqual(self.entrepreneur.node_type, 'Индивидуальный предприниматель')

    def test_max_depth_validation(self):
        """Test that hierarchy cannot be deeper than level 2."""
        with self.assertRaises(ValidationError):
            # Try to create a node supplied by a level 2 node
            deep_node = NetworkNode(name='Deep Node', supplier=self.entrepreneur)
            deep_node.clean()

    def test_self_supplier_validation(self):
        """Test that a node cannot be its own supplier."""
        with self.assertRaises(ValidationError):
            node = NetworkNode.objects.create(name='Test Node')
            node.supplier = node
            node.clean()

    def test_circular_dependency_validation(self):
        """Test that a circular dependency is not allowed."""
        with self.assertRaises(ValidationError):
            self.factory.supplier = self.entrepreneur
            self.factory.clean()

    def test_supplier_change_updates_hierarchy(self):
        """Test that changing supplier updates hierarchy level."""
        factory2 = NetworkNode.objects.create(name='Factory2')
        retail_node = NetworkNode.objects.create(name='Retail', supplier=self.factory)

        self.assertEqual(retail_node.hierarchy_level, 1)

        # Change supplier to another factory, level should remain 1
        retail_node.supplier = factory2
        retail_node.save()
        self.assertEqual(retail_node.hierarchy_level, 1)

        # Change supplier to a retail network, level should become 2
        retail_node.supplier = self.retail_network
        retail_node.save()
        self.assertEqual(retail_node.hierarchy_level, 2)