from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def login_allowed(self, request, user):
        return user.is_active and getattr(user, "is_approved", False)