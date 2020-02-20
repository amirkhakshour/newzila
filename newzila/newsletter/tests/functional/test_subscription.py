from django.urls import reverse

from newzila.testcases import WebTestCase
from newzila.newsletter.tests.factories import NewsletterFactory


class TestNewsletterViewSet(WebTestCase):
    is_anonymous = True

    def test_anonym_user_can_subscribe(self):
        newsletter = NewsletterFactory()
        kwargs = {'pk': newsletter.id}
        newsletter_url = reverse('api:newsletter-subscribe', kwargs=kwargs)
        post_params = {'email': 'dummy@example.com'}
        print("self.user", self.user)
        response = self.app.post(newsletter_url, params=post_params)
        self.assertEqual(200, response.status_code)  # for newly created instance
