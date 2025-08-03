from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from CommissionZeroApp.models import Quotation

class Command(BaseCommand):
    help = 'Delete rejected quotations older than 1 day'

    def handle(self, *args, **kwargs):
        cutoff_time = timezone.now() - timedelta(days=1)
        old_rejected_quotes = Quotation.objects.filter(status='rejected', created_at__lt=cutoff_time)
        count = old_rejected_quotes.count()
        old_rejected_quotes.delete()
        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {count} rejected quotation(s) older than 1 day."))
