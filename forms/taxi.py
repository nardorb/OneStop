import wtforms
from wtforms import validators


class TaxiForm(wtforms.Form):

  license_plate = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(min=5,max=7)])

  make = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(min=3)])

  model = wtforms.StringField(validators=[
    validators.Required(),
    validators.Length(min=3)])

  vehicle_type = wtforms.SelectField(validators=[
    validators.Required()],
    choices=[('Sedan', 'Sedan'), ('Suv', 'Suv'),
              ('Limo', 'Limo'), ('Mini Bus','Mini Bus'),
              ('Bus','Bus')])

  color = wtforms.SelectField(validators=[
    validators.Required()],
    choices=[('white', 'White'), ('black', 'Black'),
              ('red', 'Red'), ('blue','Blue'),
              ('purple','Purple'), ('silver','Silver')])

  is_operational = wtforms.BooleanField(validators=[
    validators.Required()])


  def validate_license_plate(self, field):
      field.data = field.data.strip()