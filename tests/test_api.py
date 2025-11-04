from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from network.models import NetworkNode, Product
from users.models import Employee

class NetworkNodeAPITest(APITestCase):

    def setUp(self):
        self.active_user = Employee.objects.create_user(username='active_user', password='password', is_active=True)
        self.inactive_user = Employee.objects.create_user(username='inactive_user', password='password', is_active=False)
        self.product = Product.objects.create(name='Test Product', model='Test Model', release_date='2024-01-01')
        self.factory = NetworkNode.objects.create(name='Test Factory', country='USA', debt=0)

    def test_unauthenticated_access(self):
        """Ensure unauthenticated users cannot access the API."""
        url = reverse('networknode-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_user_access(self):
        """Ensure inactive users cannot access the API."""
        self.client.login(username='inactive_user', password='password')
        url = reverse('networknode-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_network_nodes(self):
        """Ensure active users can list network nodes."""
        self.client.login(username='active_user', password='password')
        url = reverse('networknode-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_network_node(self):
        """Ensure active users can create network nodes."""
        self.client.login(username='active_user', password='password')
        url = reverse('networknode-list')
        data = {
            'name': 'New Retailer',
            'email': 'retailer@example.com',
            'country': 'Canada',
            'city': 'Toronto',
            'street': 'Yonge St',
            'house_number': '123',
            'products': []
        }
        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"API Error: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_node = NetworkNode.objects.get(name='New Retailer')
        self.assertEqual(new_node.debt, 0)

    def test_create_node_invalid_data(self):
        """Ensure API returns 400 Bad Request for invalid data."""
        self.client.login(username='active_user', password='password')
        url = reverse('networknode-list')
        # Data missing required 'name' field
        data = {
            'email': 'invalid@example.com',
            'country': 'Nowhere',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_network_node(self):
        """Ensure active users can retrieve a single network node."""
        self.client.login(username='active_user', password='password')
        url = reverse('networknode-detail', args=[self.factory.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.factory.name)

    def test_delete_network_node(self):
        """Ensure active users can delete a network node."""
        self.client.login(username='active_user', password='password')
        node_to_delete = NetworkNode.objects.create(name='To Be Deleted', country='DE')
        url = reverse('networknode-detail', args=[node_to_delete.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(NetworkNode.objects.filter(id=node_to_delete.id).exists())

    def test_update_debt_is_forbidden(self):
        """Ensure the debt field cannot be updated via the API."""
        self.client.login(username='active_user', password='password')
        url = reverse('networknode-detail', args=[self.factory.id])
        data = {'debt': '5000.00'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.factory.refresh_from_db()
        self.assertNotEqual(self.factory.debt, 5000.00)

    def test_filter_by_country(self):
        """Ensure filtering by country works."""
        self.client.login(username='active_user', password='password')
        NetworkNode.objects.create(name='Canadian Factory', country='Canada', debt=0)
        url = reverse('networknode-list') + '?country=USA'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The response is now paginated
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Factory')

    def test_pagination(self):
        """Ensure the list view is paginated."""
        # Create 15 nodes to test pagination (PAGE_SIZE is 10)
        for i in range(15):
            NetworkNode.objects.create(name=f'Node {i}', country='USA', node_type=NetworkNode.NodeType.FACTORY)
        
        self.client.login(username='active_user', password='password')
        url = reverse('networknode-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check pagination fields
        self.assertEqual(response.data['count'], 16) # 15 created + 1 from setUp
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])


class NetworkNodeIntegrationTest(APITestCase):

    def setUp(self):
        self.user = Employee.objects.create_user(username='testuser', password='password', is_active=True)
        self.product = Product.objects.create(name='Laptop', model='X1', release_date='2023-01-01')
        self.client.login(username='testuser', password='password')

    def test_full_crud_cycle(self):
        """
        Test the full lifecycle of a network node:
        1. Create a factory.
        2. Create a retail node supplied by the factory.
        3. Retrieve and verify the retail node.
        4. Filter nodes by country.
        5. Update the retail node.
        6. Delete the retail node.
        """
        # 1. Create a factory
        factory_data = {
            'name': 'Main Factory', 'email': 'factory@example.com', 'country': 'Germany',
            'city': 'Berlin', 'street': 'Factory St', 'house_number': '1',
            'products': [self.product.id]
        }
        response = self.client.post(reverse('networknode-list'), factory_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        factory_id = response.data['id']

        # 2. Create a retail node
        retail_data = {
            'name': 'Main Retailer', 'email': 'retailer@example.com', 'country': 'Germany',
            'city': 'Munich', 'street': 'Retail St', 'house_number': '10',
            'supplier': factory_id,
            'products': [self.product.id]
        }
        response = self.client.post(reverse('networknode-list'), retail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        retail_id = response.data['id']
        self.assertEqual(response.data['supplier']['id'], factory_id)

        # 3. Retrieve and verify the retail node
        response = self.client.get(reverse('networknode-detail', args=[retail_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Main Retailer')

        # 4. Filter nodes by country
        response = self.client.get(reverse('networknode-list') + '?country=Germany')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        response = self.client.get(reverse('networknode-list') + '?country=France')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        # 5. Update the retail node
        update_data = {'name': 'Updated Main Retailer'}
        response = self.client.patch(reverse('networknode-detail', args=[retail_id]), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Main Retailer')

        # 6. Delete the retail node
        response = self.client.delete(reverse('networknode-detail', args=[retail_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it's deleted
        response = self.client.get(reverse('networknode-detail', args=[retail_id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(NetworkNode.objects.count(), 1) # Only factory should remain
