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
    class NodeType(models.IntegerChoices):
        FACTORY = 0, 'Завод'
        RETAIL_NETWORK = 1, 'Розничная сеть'
        ENTREPRENEUR = 2, 'Индивидуальный предприниматель'

    node_type = models.IntegerField(choices=NodeType.choices, verbose_name='Тип звена', default=NodeType.FACTORY)
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
        if self.node_type == self.NodeType.FACTORY:
            return 0
        if not self.supplier:
            # This case should ideally not happen if validation is correct
            return 0
        return self.supplier.hierarchy_level + 1

    def clean(self):
        if self.node_type == self.NodeType.FACTORY and self.supplier is not None:
            raise ValidationError('A factory cannot have a supplier.')
        if self.supplier == self:
            raise ValidationError('A node cannot be its own supplier.')
        # Check for circular dependency
        ancestor = self.supplier
        while ancestor is not None:
            if ancestor == self:
                raise ValidationError('Circular dependency detected.')
            ancestor = ancestor.supplier

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Звено сети'
        verbose_name_plural = 'Звенья сети'
