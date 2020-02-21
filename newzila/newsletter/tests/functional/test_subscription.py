from django.urls import reverse

from newzila.testcases import WebTestCase
from newzila.newsletter.tests.factories import NewsletterFactory
from newzila.newsletter.models import Subscription


class TestNewsletterViewSet(WebTestCase):
    is_anonymous = True
    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.newsletter = NewsletterFactory()
        kwargs = {'pk': self.newsletter.id}
        self.newsletter_subscribe_url = reverse('api:newsletter-subscribe', kwargs=kwargs)

    def test_anonym_user_can_subscribe(self):
        post_params = {'email_field': 'dummy@example.com'}
        response = self.app.post_json(self.newsletter_subscribe_url, params=post_params)
        self.assertEqual(200, response.status_code)  # for newly created instance
        Subscription.objects.get(email_field=post_params['email_field'])  # creates the subscription

    def test_user_can_subscribe(self):
        user = self.user_1
        response = self.app.post_json(self.newsletter_subscribe_url, user=user)
        self.assertEqual(200, response.status_code)
        Subscription.objects.get(user=user)  # TODO check for output

    def test_user_cant_subscribe_adding_custom_email(self):
        # subscribe first
        Subscription.objects.create(newsletter=self.newsletter, email_field='dummy@example.com')
        with self.assertRaises(Exception):
            # subscribe using using custom email
            Subscription.objects.create(newsletter=self.newsletter, email_field='dummy@example.com')
