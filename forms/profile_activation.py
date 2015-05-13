import wtforms
from wtforms import validators

from forms.profile import ProfileForm


class ProfileActivationForm(ProfileForm):
  email = None

  k = wtforms.HiddenField('Activation Key', validators=[validators.Optional()])
