from django.conf import settings
from django.urls import re_path
from rest_framework.routers import DefaultRouter, SimpleRouter

from rest_framework_swagger.views import get_swagger_view

from newzila.users.api.views import UserViewSet
from newzila.newsletter.api.views import NewsletterViewSet

schema_view = get_swagger_view(title='Newzila API')

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("newsletter", NewsletterViewSet)

app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    re_path(r'^docs/', schema_view)
]
