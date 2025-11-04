from django.core.management.base import BaseCommand
from network.models import Product, NetworkNode

class Command(BaseCommand):
    help = 'Seeds the database with initial data for products and network nodes.'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')

        # Clear existing data to ensure a clean slate
        self.stdout.write('Clearing old data...')
        NetworkNode.objects.all().delete()
        Product.objects.all().delete()

        # Create Products
        self.stdout.write('Creating products...')
        product1 = Product.objects.create(name='Смартфон', model='Galaxy S25', release_date='2025-02-01')
        product2 = Product.objects.create(name='Ноутбук', model='MacBook Pro 16', release_date='2024-10-15')
        product3 = Product.objects.create(name='Наушники', model='Sony WH-1000XM6', release_date='2025-06-01')

        # Create Network Nodes
        self.stdout.write('Creating network nodes...')

        # Hierarchy 1: Factory -> Retail -> Entrepreneur
        factory1 = NetworkNode.objects.create(
            name='Завод "Электроника"',
            email='factory1@example.com',
            country='Россия', city='Москва', street='Промышленная', house_number='1',
            debt=0.00
        )
        factory1.products.add(product1, product2, product3)

        retail1 = NetworkNode.objects.create(
            name='Сеть "ТехноМир"',
            email='retail1@example.com',
            country='Россия', city='Санкт-Петербург', street='Невский проспект', house_number='28',
            supplier=factory1,
            debt=25000.75
        )
        retail1.products.add(product1, product2)

        ip1 = NetworkNode.objects.create(
            name='ИП "Гаджет Плюс"',
            email='ip1@example.com',
            country='Россия', city='Санкт-Петербург', street='Садовая', house_number='15',
            supplier=retail1,
            debt=5000.50
        )
        ip1.products.add(product1)

        # Hierarchy 2: Factory -> Entrepreneur
        factory2 = NetworkNode.objects.create(
            name='Завод "Инновации"',
            email='factory2@example.com',
            country='Беларусь', city='Минск', street='Партизанский проспект', house_number='100',
            debt=0.00
        )
        factory2.products.add(product2, product3)

        ip2 = NetworkNode.objects.create(
            name='ИП "Мобильный Уголок"',
            email='ip2@example.com',
            country='Беларусь', city='Минск', street='ул. Ленина', house_number='5',
            supplier=factory2,
            debt=1234.00
        )
        ip2.products.add(product2)

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
