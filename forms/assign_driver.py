import wtforms
from wtforms import validators
from models.taxi_driver import TaxiDriver
from models.taxi import Taxi
from models.order import Order


class AssignDriverForm(wtforms.Form):

  driver_id = wtforms.StringField(validators=[
      validators.Required(),
      validators.Length(max=10)])

  def validate_driver_id(self, field):
      field.data = field.data.strip()