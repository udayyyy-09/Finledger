from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    # Show username in responses, but don't require it on input
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Transaction
        fields = (
            'id', 'user', 'user_username',
            'amount', 'type', 'category',
            'date', 'notes',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'user', 'user_username', 'created_at', 'updated_at')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        # income-only categories shouldn't be marked as expenses — basic sanity check
        income_categories = {'salary', 'freelance', 'investment'}
        if data.get('type') == Transaction.Type.EXPENSE and data.get('category') in income_categories:
            raise serializers.ValidationError(
                f"Category '{data['category']}' doesn't make sense for an expense. Check the type."
            )
        return data