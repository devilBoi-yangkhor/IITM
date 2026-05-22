from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Ensure Google-authenticated users are always active."""
        if sociallogin.is_existing:
            user = sociallogin.user
            if not user.is_active:
                user.is_active = True
                user.save()
    
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.is_active = True
        user.save()
        return user