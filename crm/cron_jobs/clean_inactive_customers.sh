#!/bin/bash

# Go to the project root (where manage.py is)
cd "$(dirname "$0")/../.."

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

cutoff = timezone.now() - timedelta(days=365)
inactive = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff)
count = inactive.count()
inactive.delete()
print(count)
")

# Log result with timestamp
echo \"$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $DELETED_COUNT\" >> /tmp/customer_cleanup_log.txt

