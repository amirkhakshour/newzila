from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import NewsletterSerializer, SubscriptionSerializer
from ..models import Newsletter, Subscription


class NewsletterViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = NewsletterSerializer
    queryset = Newsletter.objects.all()
    permission_classes = (AllowAny,)

    slug_url_kwarg = 'newsletter_slug'

    @action(detail=True, methods=["POST"])
    def subscribe(self, request, pk, *args, **kwargs):
        _data = {}
        _data.update(request.data)

        # append last to prevent user overriding
        _data.update({
            'newsletter': pk,
            'user': request.user.pk,
        })

        context = self.get_serializer_context()
        serializer = SubscriptionSerializer(data=_data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path='(?P<newsletter_slug>[^/.]+)/verify/(?P<token>[^/.]+)')
    def verification(self, request, newsletter_slug, token):
        """Why use slug instead of IDs? since the slugs are more reliable when migrating data"""
        newsletter = get_object_or_404(
            Newsletter, slug=newsletter_slug
        )

        get_object_or_404(
            Subscription, newsletter=newsletter,
            verification_token=token
        )
        return Response(status=status.HTTP_200_OK)
