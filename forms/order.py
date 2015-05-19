import wtforms
from wtforms import validators


class OrderForm(wtforms.Form):

  origin = wtforms.StringField(validators=[
      validators.Required()])

  destination = wtforms.StringField(validators=[
      validators.Required()])

  passengers = wtforms.StringField(validators=[
    validators.Required()])

  comments = wtforms.StringField(validators=[
      validators.Optional()])

  vehicle_type = wtforms.SelectField(validators=[
    validators.Required()],
    choices=[('Sedan', 'Sedan'), ('SUV', 'SUV'), ('Corporate', 'Corporate'),
              ('Luxury', 'Luxury'), ('Mini Bus','Mini Bus'),
              ('Bus','Bus')])

  cost = wtforms.StringField(validators=[
      validators.Optional()])


  def validate_origin(self, field):
      field.data = field.data.strip()

  def validate_destination(self, field):
      field.data = field.data.strip()