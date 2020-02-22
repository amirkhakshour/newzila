from django.urls import reverse
from django.core import mail

from newzila.testcases import WebTestCase, EmailsMixin
from newzila.newsletter.tests.factories import NewsletterFactory
from newzila.newsletter.models import Subscription


class TestNewsletterViewSet(EmailsMixin, WebTestCase):
    is_anonymous = True
    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.newsletter = NewsletterFactory()
        kwargs = {'slug': self.newsletter.slug}
        self.newsletter_subscribe_url = reverse('api:newsletter-subscribe', kwargs=kwargs)
        self.newsletter_unsubscribe_url = reverse('api:newsletter-unsubscribe', kwargs=kwargs)

    def test_anonym_user_can_subscribe(self):
        post_params = {'email_field': 'dummy@example.com'}
        response = self.app.post_json(self.newsletter_subscribe_url, params=post_params)
        self.assertEqual(200, response.status_code)  # for newly created instance
        Subscription.objects.get(email_field=post_params['email_field'])  # creates the subscription

    def test_user_can_subscribe(self):
        user = self.user_1
        response = self.app.post_json(self.newsletter_subscribe_url, user=user)
        self.assertEqual(200, response.status_code)
        assert Subscription.objects.get(user=user)  # TODO check for output

    def test_user_cant_subscribe_adding_custom_email(self):
        # subscribe first
        # todo move to unit tests
        Subscription.objects.create(newsletter=self.newsletter, email_field='dummy@example.com')
        with self.assertRaises(Exception):
            # subscribe using using custom email
            Subscription.objects.create(newsletter=self.newsletter, email_field='dummy@example.com')

    def test_email_sent_after_user_subscription(self):
        user = self.user_1
        response = self.app.post_json(self.newsletter_subscribe_url, user=self.user_1)
        subscription = Subscription.objects.get(newsletter=self.newsletter, user=user)
        self.assertEqual(200, response.status_code)  # for newly created instance
        self._test_common_part(subscription.email)

        # Check subject
        expected_subject = '{} - Confirm subscription'.format(self.newsletter.title)
        self.assertEqual(expected_subject, mail.outbox[0].subject)

        # Check verification URL
        self.assertIn(subscription.subscribe_verification_url(), mail.outbox[0].body)

    def test_verified_and_active_after_verification(self):
        user = self.user_1
        self.app.post_json(self.newsletter_subscribe_url, user=self.user_1)
        subscription = Subscription.objects.get(newsletter=self.newsletter, user=user)
        response = self.app.get(subscription.subscribe_verification_url())

        subscription.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertTrue(subscription.is_active)
        self.assertIsNotNone(subscription.verification_date)

    def test_subscribed_after_verification(self):
        user = self.user_1
        self.app.post_json(self.newsletter_subscribe_url, user=user)
        subscription = Subscription.objects.get(newsletter=self.newsletter, user=user)

        response = self.app.get(subscription.subscribe_verification_url())

        subscription.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertTrue(subscription.is_active)
        self.assertIsNotNone(subscription.verification_date)

    def test_user_can_unsubscribe(self):
        user = self.user_1
        self.app.post_json(self.newsletter_subscribe_url, user=user)  # create
        subscription = Subscription.objects.get(newsletter=self.newsletter, user=user)
        self.app.get(subscription.subscribe_verification_url())  # verify
        response = self.app.get(self.newsletter_unsubscribe_url, user=user)

        subscription.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertFalse(subscription.is_active)

    def test_anonym_can_unsubscribe(self):
        post_params = {'email_field': 'dummy@example.com'}
        self.app.post_json(self.newsletter_subscribe_url, params=post_params)
        subscription = Subscription.objects.get(newsletter=self.newsletter, **post_params)
        self.app.get(subscription.subscribe_verification_url())  # verify
        response = self.app.get(self.newsletter_unsubscribe_url)

        subscription.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertFalse(subscription.is_active)

    def test_user_cant_unsubscribe_unverified_subscription(self):
        """
        We can't unsubscribe a not verified subscription
        TODO
        """
