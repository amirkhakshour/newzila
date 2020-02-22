from factory import DjangoModelFactory, Faker, Sequence, SubFactory
from newzila.users.tests.factories import UserFactory
from newzila.newsletter.models import Newsletter, Subscription


class NewsletterFactory(DjangoModelFactory):
    title = Sequence(lambda n: "NewsLetter %03d" % n)
    slug = Sequence(lambda n: "newsletter-%03d" % n)
    email = Sequence(lambda n: "sender-%03d@example.com" % n)
    sender = Sequence(lambda n: "Sender %03d" % n)

    class Meta:
        model = Newsletter


class SubscriptionAnonymousFactory(DjangoModelFactory):
    newsletter = SubFactory(NewsletterFactory)
    email = Faker("email")
    name = Sequence(lambda n: "Receiver %03d" % n)
    user = None

    class Meta:
        model = Subscription
        django_get_or_create = ["newsletter"]


class SubscriptionFactory(SubscriptionAnonymousFactory):
    user = SubFactory(UserFactory)

    class Meta:
        model = Subscription
        django_get_or_create = ["newsletter"]
