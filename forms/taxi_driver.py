import wtforms
from wtforms import validators


class TaxiDriverForm(wtforms.Form):

    first_name = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(min=3,max=12)])

    last_name = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(min=3,max=15)])

    driver_id = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(max=9)])

    sex = wtforms.StringField(validators=[
      validators.Required()])

    email = wtforms.StringField(validators=[
      validators.Required()])

    tel_number = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(min=7,max=11)])

    parish = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(min=3)])

    address = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(min=3)])

    #later converted to date field
    dob = wtforms.StringField(validators=[
      validators.Required()])

    password = wtforms.PasswordField(validators=[
      validators.Required(),
      validators.Length(min=6),
      validators.EqualTo('password_confirmation',
                         message='Passwords must match')])

    password_confirmation = wtforms.PasswordField()


    def validate_driver_id(self, field):
      field.data = field.data.strip()

    def validate_first_name(self, field):
      field.data = field.data.strip()

    def validate_last_name(self, field):
      field.data = field.data.strip()