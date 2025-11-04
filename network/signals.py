from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import NetworkNode
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=NetworkNode)
def log_supplier_change(sender, instance, **kwargs):
    """Logs a message when a node's supplier is about to change."""
    if instance.pk:  # Check if this is an update
        try:
            old_instance = NetworkNode.objects.get(pk=instance.pk)
            if old_instance.supplier != instance.supplier:
                logger.info(
                    f"Supplier for {instance.name} (ID: {instance.id}) will be changed "
                    f"from {old_instance.supplier} to {instance.supplier}."
                )
        except NetworkNode.DoesNotExist:
            # Should not happen in pre_save for an existing object
            pass