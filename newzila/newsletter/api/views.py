from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import NewsletterSerializer
from ..models import Newsletter


class NewsletterViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = NewsletterSerializer
    queryset = Newsletter.objects.all()
    permission_classes = (AllowAny,)

    @action(detail=True, methods=["POST"])
    def subscribe(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
