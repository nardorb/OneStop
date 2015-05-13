import decimal
import re

from wtforms import ValidationError


class DecimalPlaces(object):
  """Validates the number of decimal places entered in a field."""

  def __init__(self, places=2, message=None):
    self.places = places
    self.message = message

  def __call__(self, form, field):
    if not isinstance(field.data, decimal.Decimal):
      raise ValidationError('Expected decimal.Decimal, got %s.'
                            % type(field.data))

    regex = r'^\d+\.\d{%d}$' % self.places

    if not re.match(regex, field.raw_data[0]):
      raise ValidationError('Field must have %d decimal places.' % self.places)
