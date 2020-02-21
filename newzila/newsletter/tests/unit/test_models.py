from django.test import TestCase

from newzila.newsletter.tests.factories import NewsletterFactory
from newzila.users.tests.factories import UserFactory
from newzila.newsletter.models import Subscription


class SubscriptionModelTest(TestCase):
    def setUp(self):
        super().setUp()
        self.newsletter = NewsletterFactory()
        self.subscriber_1 = UserFactory(username='subscriber_1')

    def test_raises_if_no_email_and_user(self):
        """We can't save a subscription that has no user or an email"""
        with self.assertRaisesRegex(Exception, "^Neither an email nor a username is set"):
            Subscription.objects.create(newsletter=self.newsletter)

    def test_raises_if_both_email_and_user(self):
        """We can't save a subscription that has both user and email"""
        Subscription.objects.create(newsletter=self.newsletter, email_field='dummy@example.com')
        Subscription.objects.create(newsletter=self.newsletter, user=self.subscriber_1)

        with self.assertRaisesRegex(Exception, "^If user is set, email must be null and"):
            Subscription.objects.create(newsletter=self.newsletter, user=self.subscriber_1,
                                        email_field='dummy@example.com')

    def test_raises_if_multiple_subscription_for_same_newsletter(self):
        """We can't add multiple subscription for the same newsletter for the same user/email_field"""
        Subscription.objects.create(newsletter=self.newsletter, email_field='dummy@example.com')

        with self.assertRaises(Exception):
            Subscription.objects.create(newsletter=self.newsletter, email_field='dummy@example.com')
