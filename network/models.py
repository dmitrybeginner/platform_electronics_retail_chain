from django.db import models
from django.core.exceptions import ValidationError

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название продукта')
    model = models.CharField(max_length=255, verbose_name='Модель продукта')
    release_date = models.DateField(verbose_name='Дата выхода на рынок')

    def __str__(self):
        return f"{self.name} {self.model}"

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

class NetworkNode(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    email = models.EmailField(verbose_name='Email')
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house_number = models.CharField(max_length=20, verbose_name='Номер дома')
    products = models.ManyToManyField(Product, verbose_name='Продукты', blank=True)
    supplier = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Поставщик')
    debt = models.DecimalField(max_digits=19, decimal_places=2, default=0, verbose_name='Задолженность перед поставщиком')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    @property
    def hierarchy_level(self):
        if not self.supplier:
            return 0
        return self.supplier.hierarchy_level + 1

    @property
    def node_type(self):
        level = self.hierarchy_level
        if level == 0:
            return 'Завод'
        elif level == 1:
            return 'Розничная сеть'
        elif level == 2:
            return 'Индивидуальный предприниматель'
        return 'Неопределенный тип'

    def clean(self):
        # Check for self-reference first to prevent recursion
        if self.supplier == self:
            raise ValidationError('A node cannot be its own supplier.')

        # Check for circular dependency before accessing hierarchy_level
        ancestor = self.supplier
        while ancestor is not None:
            if ancestor == self:
                raise ValidationError('Circular dependency detected.')
            ancestor = ancestor.supplier

        # Now it's safe to check the hierarchy depth
        if self.supplier and self.supplier.hierarchy_level >= 2:
            raise ValidationError('The hierarchy cannot be deeper than 3 levels (Factory -> Retail -> Entrepreneur).')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Звено сети'
        verbose_name_plural = 'Звенья сети'
