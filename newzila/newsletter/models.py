from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from .utils import make_verification_token

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Newsletter(models.Model):
    """
    Stores all information about a specific newsletter.
    :title: title of Newsletter
    :slug: slug of Newsletter for resolving Newsletter URL
    :email: The sender email, used to create `from_email` variable
    :sender: The sender name, used to create `from_email` variable
    """
    title = models.CharField(
        max_length=200, verbose_name=_('newsletter title')
    )
    slug = models.SlugField(db_index=True, unique=True)
    email = models.EmailField(
        verbose_name=_('e-mail'), help_text=_('Sender e-mail')
    )
    sender = models.CharField(
        max_length=200, verbose_name=_('sender'), help_text=_('Sender name')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')


class Subscription(models.Model):
    """
    Holds all information about a specific newsletter subscription.

    :user: The user, that has subscribed. None if anonymous.
    :email_field: Email of the user if the user is anonymous.
    :name_field: Name of the user if the user is anonymous.
    :email: The subscribed email. Takes precedence of the user.email.
    :create_date: The date of the subscription.

    Note: if the user is_authenticated, email and name fields use the user field as their reference,
        email_field and name_field will be ignored. Otherwise, they will be used for storing user related info.
    """
    newsletter = models.ForeignKey(
        Newsletter, verbose_name=_('newsletter'), on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        AUTH_USER_MODEL, blank=True, null=True, verbose_name=_('user'),
        on_delete=models.CASCADE
    )

    email_field = models.EmailField(
        db_column='email', verbose_name=_('e-mail'), db_index=True,
        blank=True, null=True
    )
    name_field = models.CharField(
        db_column='name', max_length=30, blank=True, null=True,
        verbose_name=_('name'), help_text=_('optional')
    )

    create_date = models.DateTimeField(editable=False, default=now)

    verification_token = models.CharField(
        verbose_name=_('verification_token'), max_length=40,
        default=make_verification_token
    )
    verification_date = models.DateTimeField(
        verbose_name=_('Verification date'), blank=True, null=True)

    @property
    def email(self):
        if self.user:
            return self.user.email
        return self.email_field

    @email.setter
    def email(self, email):
        if not self.user:
            self.email_field = email

    @property
    def name(self):
        if self.user:
            return self.user.get_full_name()
        return self.name_field

    @name.setter
    def name(self, name):
        if not self.user:
            self.name_field = name

    def __str__(self):
        if self.name:
            return _(u"%(name)s <%(email)s> to %(newsletter)s") % {
                'name': self.name,
                'email': self.email,
                'newsletter': self.newsletter
            }

        else:
            return _(u"%(email)s to %(newsletter)s") % {
                'email': self.email,
                'newsletter': self.newsletter
            }

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        unique_together = ('user', 'email_field', 'newsletter')

    def save(self, *args, **kwargs):
        """
        Perform some validation and state maintenance of Subscription.
        """
        self.pre_save_check(*args, **kwargs)
        super(Subscription, self).save(*args, **kwargs)

    def pre_save_check(self, *args, **kwargs):
        assert self.user or self.email_field, \
            _('Neither an email nor a username is set. This asks for '
              'inconsistency!')

        assert ((self.user and not self.email_field) or
                (self.email_field and not self.user)), \
            _('If user is set, email must be null and vice versa.')

        assert not self.already_subscribed()

    def already_subscribed(self):
        if self.pk is not None:  # modifying/saving already created subscriptions
            return False
        return Subscription.objects.filter(newsletter_id=self.newsletter.pk). \
            filter(models.Q(email_field=self.email) | models.Q(user=self.user)).exists()
