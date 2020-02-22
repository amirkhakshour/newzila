from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings
from newzila.users.api.views import UserViewSet
from newzila.newsletter.api.views import NewsletterViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("newsletter", NewsletterViewSet)

app_name = "api"
urlpatterns = router.urls
