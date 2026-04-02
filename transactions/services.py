# Business logic lives here — not in views, not in models. This makes it testable and reusable.

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from decimal import Decimal
from .models import Transaction


def get_summary(queryset):
    """
    Given a queryset of transactions, compute the core financial summary.
    This is the main analytics function — called by the summary endpoint.
    """
    totals = queryset.aggregate(
        total_income=Sum('amount', filter=Q(type='income')),
        total_expenses=Sum('amount', filter=Q(type='expense')),
        total_count=Count('id'),
    )

    total_income = totals['total_income'] or Decimal('0.00')
    total_expenses = totals['total_expenses'] or Decimal('0.00')
    balance = total_income - total_expenses

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'transaction_count': totals['total_count'],
    }


def get_category_breakdown(queryset):
    """
    Group by category and sum amounts.
    Returns separate breakdowns for income and expense categories.
    """
    breakdown = (
        queryset
        .values('category', 'type')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('type', '-total')
    )
    return list(breakdown)


def get_monthly_totals(queryset):
    """
    Monthly income vs expense summary — useful for charts on a dashboard.
    """
    monthly = (
        queryset
        .annotate(month=TruncMonth('date'))
        .values('month', 'type')
        .annotate(total=Sum('amount'))
        .order_by('month', 'type')
    )

    # restructure into {month: {income: X, expense: Y}} for easier frontend consumption
    result = {}
    for row in monthly:
        month_key = row['month'].strftime('%Y-%m')
        if month_key not in result:
            result[month_key] = {'income': Decimal('0.00'), 'expense': Decimal('0.00')}
        result[month_key][row['type']] = row['total']

    return result


def get_recent_activity(queryset, limit=10):
    """Last N transactions, most recent first."""
    return queryset.order_by('-date', '-created_at')[:limit]