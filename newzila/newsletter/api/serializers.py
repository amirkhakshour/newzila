from rest_framework import serializers
from ..models import Newsletter, Subscription


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ["title", "slug", "email", "sender"]  # Don't try to use __all__!


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'newsletter',
            'user',
            'email_field',
            'name_field',
        ]
