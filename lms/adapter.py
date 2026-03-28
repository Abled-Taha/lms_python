from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

class NoSignupAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.
        """
        return False