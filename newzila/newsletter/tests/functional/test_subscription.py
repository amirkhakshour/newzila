from django.urls import reverse

from newzila.testcases import WebTestCase
from newzila.newsletter.tests.factories import NewsletterFactory
from newzila.newsletter.models import Subscription


class TestNewsletterViewSet(WebTestCase):
    is_anonymous = True
    csrf_checks = False

    def test_anonym_user_can_subscribe(self):
        newsletter = NewsletterFactory()
        kwargs = {'pk': newsletter.id}
        newsletter_url = reverse('api:newsletter-subscribe', kwargs=kwargs)
        post_params = {'email_field': 'dummy@example.com'}
        response = self.app.post_json(newsletter_url, params=post_params)
        self.assertEqual(200, response.status_code)  # for newly created instance
        Subscription.objects.get(email_field=post_params['email_field'])  # creates the subscription

    def test_user_can_subscribe(self):
        newsletter = NewsletterFactory()
        kwargs = {'pk': newsletter.id}
        newsletter_url = reverse('api:newsletter-subscribe', kwargs=kwargs)
        user = self.user_1
        response = self.app.post_json(newsletter_url, user=user)
        self.assertEqual(200, response.status_code)
        Subscription.objects.get(user=user)
