from mezzanine.accounts.forms import ProfileForm
from captcha.fields import CaptchaField


class ProfileFormCustom(ProfileForm):
    captcha = CaptchaField()
