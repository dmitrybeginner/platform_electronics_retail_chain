from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.urls import reverse
from network.models import NetworkNode
from users.models import Employee
from network.admin import NetworkNodeAdmin

class NetworkNodeAdminTest(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = NetworkNodeAdmin(NetworkNode, self.site)
        self.factory = RequestFactory()

        # Create users
        self.superuser = Employee.objects.create_superuser(username='admin', password='password')
        
        # Create network nodes
        self.factory_node = NetworkNode.objects.create(name='Завод', city='Минск', debt=1000.00)
        self.retail_network = NetworkNode.objects.create(name='Розничная сеть', supplier=self.factory_node, city='Москва', debt=500.00)

    def test_clear_debt_action(self):
        """Test the clear_debt admin action."""
        request = self.factory.post('/')
        request.user = self.superuser
        
        queryset = NetworkNode.objects.filter(id=self.retail_network.id)
        self.admin.clear_debt(request, queryset)
        
        self.retail_network.refresh_from_db()
        self.assertEqual(self.retail_network.debt, 0)

    def test_get_supplier_link(self):
        """Test the get_supplier_link method."""
        # Test with a supplier
        link = self.admin.get_supplier_link(self.retail_network)
        expected_link = reverse("admin:network_networknode_change", args=[self.factory_node.id])
        self.assertIn(expected_link, link)
        self.assertIn(self.factory_node.name, link)

        # Test without a supplier
        link_no_supplier = self.admin.get_supplier_link(self.factory_node)
        self.assertEqual(link_no_supplier, "-")

    def test_city_filter(self):
        """Test filtering by city in the admin list view."""
        self.client.login(username='admin', password='password')
        url = reverse('admin:network_networknode_changelist')

        # Test filtering for 'Москва'
        response = self.client.get(url, {'city': 'Москва'})
        self.assertEqual(response.status_code, 200)
        queryset = response.context['cl'].queryset
        self.assertIn(self.retail_network, queryset)
        self.assertNotIn(self.factory_node, queryset)
        self.assertEqual(queryset.count(), 1)

        # Test filtering for 'Минск'
        response = self.client.get(url, {'city': 'Минск'})
        self.assertEqual(response.status_code, 200)
        queryset = response.context['cl'].queryset
        self.assertIn(self.factory_node, queryset)
        self.assertNotIn(self.retail_network, queryset)
        self.assertEqual(queryset.count(), 1)

    def test_search_fields(self):
        """Test the search fields in the admin list view."""
        self.client.login(username='admin', password='password')
        url = reverse('admin:network_networknode_changelist')

        # Search for the factory by name
        response = self.client.get(url, {'q': 'Завод'})
        self.assertEqual(response.status_code, 200)
        queryset = response.context['cl'].queryset
        self.assertIn(self.factory_node, queryset)
        self.assertNotIn(self.retail_network, queryset)
        self.assertEqual(queryset.count(), 1)