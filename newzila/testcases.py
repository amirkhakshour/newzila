from django_webtest import WebTest
from django.contrib.auth import get_user_model

User = get_user_model()


class WebTestCase(WebTest):
    is_staff = False
    is_anonymous = False
    is_superuser = False

    username = 'testuser'
    email = 'testuser@buymore.com'
    password = 'somefancypassword'
    permissions = []

    def setUp(self):
        self.user = None

        if not self.is_anonymous:
            self.user = self.create_user(
                self.username, self.email, self.password)
            self.user.is_staff = self.is_staff
            self.user.save()

    def create_user(self, username=None, email=None, password=None):
        """
        Create a user for use in a test.

        As usernames are optional in newer versions of Django, it only sets it
        if exists.
        """
        kwargs = {'email': email, 'password': password}
        fields = {f.name: f for f in User._meta.get_fields()}

        if 'username' in fields:
            kwargs['username'] = username
        return User.objects.create_user(**kwargs)

    def get(self, url, **kwargs):
        kwargs.setdefault('user', self.user)
        return self.app.get(url, **kwargs)

    def post(self, url, **kwargs):
        kwargs.setdefault('user', self.user)
        return self.app.post(url, **kwargs)
