from allauth.account.forms import SignupForm

class SignupFormUsernameFocus(SignupForm):
    # switch autofocus to email
    # https://github.com/pennersr/django-allauth/issues/575
    def __init__(self, *args, **kwargs):
        super(SignupFormUsernameFocus, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs["autofocus"] = 'autofocus'
        self.fields['username'].widget.attrs.pop("autofocus", None)
