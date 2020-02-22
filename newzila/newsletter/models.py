from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.template.loader import select_template
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.contrib.sites.models import Site

from rest_framework.exceptions import ValidationError as APIValidationError

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

    TEMPLATE_ROOT = 'newsletter/message/'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')

    def get_templates(self):
        """
        Returns a subject, text, HTML templates tuple for sending subscription email
        """
        tpl_subst = {
            'newsletter': self.slug
        }

        subject_template = select_template([
            self.TEMPLATE_ROOT + '%(newsletter)s/subject.txt' % tpl_subst,
            self.TEMPLATE_ROOT + 'subject.txt',  # global template for subject message
        ])

        text_template = select_template([
            self.TEMPLATE_ROOT + '%(newsletter)s/text.txt' % tpl_subst,
            self.TEMPLATE_ROOT + 'text.txt',
        ])

        html_template = select_template([
            self.TEMPLATE_ROOT + '%(newsletter)s/text.html' % tpl_subst,
            self.TEMPLATE_ROOT + 'text.html',
        ])
        return subject_template, text_template, html_template


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

    is_active = models.BooleanField(default=False, blank=True)

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
        if not (self.user or self.email_field):
            raise APIValidationError(_('Neither an email nor a username is set. This asks for '
                                       'inconsistency!'))

        if not ((self.user and not self.email_field) or
                (self.email_field and not self.user)):
            raise APIValidationError(_('If user is set, email must be null and vice versa.'))

        if self.already_subscribed():
            raise APIValidationError(_('Already subscribed!'))

    def already_subscribed(self):
        if self.pk is not None:  # modifying/saving already created subscriptions
            return False
        q = Subscription.objects.filter(newsletter_id=self.newsletter.pk)
        if self.user:
            q = q.filter(user=self.user)
        else:
            q = q.filter(email_field__exact=self.email)
        return q.exists()

    def send_verification_email(self):
        email_context = {
            'subscription': self,
            'newsletter': self.newsletter,
            'date': self.create_date,
            'site': Site.objects.get_current(),
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL
        }

        (subject_template, text_template, html_template) = self.newsletter.get_templates()
        subject = subject_template.render(email_context).strip()
        text = text_template.render(email_context)

        message = EmailMultiAlternatives(
            subject, text,
            from_email=self.newsletter.email,
            to=[self.email]
        )
        message.attach_alternative(
            html_template.render(email_context), "text/html"
        )
        message.send()

    def subscribe_verification_url(self):
        return reverse('api:newsletter-verification', kwargs={
            'slug': self.newsletter.slug,
            'token': self.verification_token
        })

    def subscribe_verify(self):
        if self.is_active:
            return
        self.verification_date = now()
        self.is_active = True
        self.save()

    def subscribe_unsubscribe(self):
        if self.verification_date is None:
            APIValidationError(_("Your subscription is not verified"))
        self.is_active = False
        self.save()
