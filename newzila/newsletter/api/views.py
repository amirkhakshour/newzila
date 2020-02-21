from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import NewsletterSerializer, SubscriptionSerializer
from ..models import Newsletter


class NewsletterViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = NewsletterSerializer
    queryset = Newsletter.objects.all()
    permission_classes = (AllowAny,)

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
