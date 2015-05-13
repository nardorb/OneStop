import webapp2_extras
import wtforms
from wtforms import validators, ValidationError


class ProfileForm(wtforms.Form):

  first_name = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(max=500)])

  last_name = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(max=500)])

  email = wtforms.StringField(validators=[
      validators.Required(),
      validators.Email()])

  tel_number = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(max=12)])

  password = wtforms.PasswordField(validators=[
      validators.Required(),
      validators.Length(min=6),
      validators.EqualTo('password_confirmation',
                         message='Passwords must match')])

  password_confirmation = wtforms.PasswordField()

  def validate_email(self, field):
    UserModel = webapp2_extras.auth.get_auth().store.user_model
    if UserModel.get_by_auth_id(field.data):
      raise ValidationError('That e-mail is aready in use!')
