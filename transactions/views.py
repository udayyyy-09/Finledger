# transactions/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Transaction
from .serializers import TransactionSerializer
from .filters import TransactionFilter
from .services import get_summary, get_category_breakdown, get_monthly_totals, get_recent_activity
from users.permissions import IsAdmin, IsAnalystOrAbove


class TransactionViewSet(viewsets.ModelViewSet):

    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['notes', 'category']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin():
            return Transaction.objects.all().select_related('user')
        return Transaction.objects.filter(user=user).select_related('user')

    def get_permissions(self):
        """
        list, retrieve       → any logged in user (viewer, analyst, admin)
        create, update, etc  → admin only
        analytics actions    → analyst or above
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            permission_classes = [IsAdmin]

        elif self.action in ('summary', 'category_breakdown', 'monthly_totals'):
            permission_classes = [IsAnalystOrAbove]

        else:
            # list, retrieve, recent — any authenticated user can access
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        qs = self.filter_queryset(self.get_queryset())
        data = get_summary(qs)
        return Response(data)

    @action(detail=False, methods=['get'], url_path='category-breakdown')
    def category_breakdown(self, request):
        qs = self.filter_queryset(self.get_queryset())
        data = get_category_breakdown(qs)
        return Response(data)

    @action(detail=False, methods=['get'], url_path='monthly-totals')
    def monthly_totals(self, request):
        qs = self.filter_queryset(self.get_queryset())
        data = get_monthly_totals(qs)
        return Response(data)

    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        qs = self.get_queryset()
        limit = int(request.query_params.get('limit', 10))
        transactions = get_recent_activity(qs, limit=limit)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
