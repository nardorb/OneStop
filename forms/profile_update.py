import wtforms
from wtforms import validators, ValidationError

from forms.profile import ProfileForm
from models.profile import Profile


class ProfileUpdateForm(ProfileForm):

  password = wtforms.PasswordField(validators=[
      validators.Optional(),
      validators.Length(min=6),
      validators.EqualTo('password_confirmation',
                         message='Passwords must match')])
  profile_id = None

  def validate_email(self, field):
    profile = Profile.get_by_email(field.data)
    if profile and profile.key().id() != self.profile_id:
      raise ValidationError("Email already in use!")
