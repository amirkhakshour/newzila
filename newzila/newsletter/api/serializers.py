from rest_framework import serializers
from ..models import Newsletter


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ["title", "slug", "email", "sender"]  # Don't try to use __all__!
