# It creates test users and fake transactions so I can test everything immediately.
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from transactions.models import Transaction
from datetime import date, timedelta
import random

User = get_user_model()

print("Clearing old data...")
Transaction.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

print("Creating users...")
admin = User.objects.create_user('admin_user', 'admin@test.com', 'Admin@1234', role='admin')
analyst = User.objects.create_user('analyst_user', 'analyst@test.com', 'Analyst@1234', role='analyst')
viewer = User.objects.create_user('viewer_user', 'viewer@test.com', 'Viewer@1234', role='viewer')

print("Creating transactions...")

categories_income = ['salary', 'freelance', 'investment']
categories_expense = ['food', 'rent', 'utilities', 'transport', 'entertainment', 'shopping', 'other']

base_date = date.today()

for i in range(50):
    is_income = random.random() > 0.4
    t_type = 'income' if is_income else 'expense'
    category = random.choice(categories_income if is_income else categories_expense)
    amount = round(random.uniform(100, 5000 if is_income else 1500), 2)
    txn_date = base_date - timedelta(days=random.randint(0, 180))

    Transaction.objects.create(
        user=random.choice([admin, analyst, viewer]),
        amount=amount,
        type=t_type,
        category=category,
        date=txn_date,
        notes=f"Auto-seeded {t_type} entry #{i+1}",
    )

print("Done! Users created:")
print("  admin_user / Admin@1234 (admin)")
print("  analyst_user / Analyst@1234 (analyst)")
print("  viewer_user / Viewer@1234 (viewer)")