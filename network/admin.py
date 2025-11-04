from django.contrib import admin
from django.db.models import Case, When, Value, IntegerField
from django.urls import reverse
from django.utils.html import format_html
from .models import Product, NetworkNode

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'release_date')
    search_fields = ('name', 'model')

@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', 'display_level', 'get_supplier_link', 'email', 'country', 'city', 'debt', 'created_at')
    list_filter = ('city', 'node_type')
    search_fields = ('name', 'email')
    actions = ['clear_debt']
    list_select_related = ('supplier',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Annotate with a level for sorting, as ordering by property is not supported.
        queryset = queryset.annotate(
            level=Case(
                When(supplier__isnull=True, then=Value(0)),
                When(supplier__supplier__isnull=True, then=Value(1)),
                When(supplier__supplier__supplier__isnull=True, then=Value(2)),
                default=Value(3), # Fallback for deeper levels
                output_field=IntegerField(),
            )
        )
        return queryset

    @admin.display(description='Уровень иерархии', ordering='level')
    def display_level(self, obj):
        # We display the property from the model, which is always correct.
        return obj.hierarchy_level

    def get_supplier_link(self, obj):
        if obj.supplier:
            link = reverse("admin:network_networknode_change", args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', link, obj.supplier.name)
        return "-"
    get_supplier_link.short_description = 'Поставщик'

    def clear_debt(self, request, queryset):
        queryset.update(debt=0)
    clear_debt.short_description = 'Очистить задолженность перед поставщиком'
