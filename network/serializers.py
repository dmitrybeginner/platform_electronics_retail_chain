from rest_framework import serializers
from .models import Product, NetworkNode


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# A simple serializer for nested supplier representation to avoid infinite recursion.
# It will only show the supplier's ID and name.
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkNode
        fields = ('id', 'name')


# New Read-only Serializer with nested objects
class NetworkNodeReadSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    supplier = SupplierSerializer(read_only=True)

    class Meta:
        model = NetworkNode
        fields = ('id', 'name', 'node_type', 'hierarchy_level', 'email', 'country', 'city', 'street', 'house_number', 'products', 'supplier', 'debt',
                  'created_at')


# The old NetworkNodeSerializer becomes the Write-only Serializer
class NetworkNodeWriteSerializer(serializers.ModelSerializer):
    # This remains as PrimaryKeyRelatedField for writing (accepting IDs)
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all(), required=False)

    class Meta:
        model = NetworkNode
        # We don't need to show all fields on write, just the ones that are writeable.
        fields = ('name', 'node_type', 'email', 'country', 'city', 'street', 'house_number', 'products', 'supplier')
        # The debt field is correctly not included here, so it can't be written.
        # read_only_fields is not strictly necessary if we list the fields explicitly,
        # but it adds an extra layer of protection.
        read_only_fields = ('debt',)

    def to_representation(self, instance):
        # When a write operation is successful, it returns a response.
        # We want that response to be in the 'read' format.
        serializer = NetworkNodeReadSerializer(instance)
        return serializer.data
