import wtforms
from wtforms import validators


class ContactForm(wtforms.Form):

  name = wtforms.TextField(validators=[validators.Required()])
  email = wtforms.TextField(validators=[validators.Required(),
                                        validators.Email()])
  topic = wtforms.TextField(validators=[validators.Required()])
  message = wtforms.TextAreaField(validators=[validators.Required()])
