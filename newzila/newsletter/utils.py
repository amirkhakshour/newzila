""" Generic helper functions """

from django.utils.crypto import get_random_string


def make_verification_token():
    """ Generate a unique verification token. """
    return get_random_string(length=40)
