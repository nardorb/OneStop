from webapp2_extras import security

from handlers import base
from library import messages
from models.profile import Profile
from forms.profile import ProfileForm
from forms.profile_update import ProfileUpdateForm


class EditorHandler(base.BaseHandler):

  def create(self):
    form = ProfileForm(self.request.POST)

    if self.request.method == 'POST' and form.validate():
      name = ' '.join([form.first_name.data,
                       form.last_name.data])

      # Create the webapp2_extras.auth user.
      model = self.auth.store.user_model
      ok, user = model.create_user(form.data['email'],
                                   password_raw=form.data['password'])

      if not ok:
        self.session.add_flash(messages.EDITOR_CREATE_ERROR,
                               level='error')
        return self.redirect_to('editors.list')

      # Create the profile.
      profile = Profile(name=name,
                        email=form.data['email'],
                        is_editor=True,
                        auth_user_id=user.key.id())
      profile.put()

      # Force reload of profile object
      Profile.get(profile.key())

      self.session.add_flash(messages.EDITOR_CREATE_SUCCESS)
      return self.redirect_to('editors.list')

    return self.render_to_response('editors/form.haml', {'form': form})

  def delete(self, id):
    editor = Profile.get_by_id(int(id))
    if not editor or not editor.is_editor:
      self.session.add_flash(messages.EDITOR_NOT_FOUND, level='error')
      return self.redirect_to('editors.list')

    editor.delete()
    self.session.add_flash(messages.EDITOR_DELETE_SUCCESS)
    return self.redirect_to('editors.list')

  def list(self):
    editors = Profile.all().filter('is_editor = ', True)
    return self.render_to_response('editors/list.haml', {'editors': editors})

  def update(self, id):
    editor = Profile.get_by_id(int(id))
    if not editor or not editor.is_editor:
      self.session.add_flash(messages.EDITOR_NOT_FOUND, level='error')
      self.redirect_to('editors.list')

    form = ProfileUpdateForm(self.request.POST, obj=editor)
    form.user_id = editor.key().id()

    if self.request.method == 'GET':
      names = editor.name.split(' ')
      form.first_name.data = names[0]
      form.last_name.data = names[1]

    form.profile_id = editor.key().id()

    if self.request.method == 'POST' and form.validate():
      # Access to the user model is only needed in this section.
      user = editor.get_auth_user()
      editor.name = ' '.join([form.first_name.data, form.last_name.data])

      if form.email.data != editor.email:
        user.auth_ids.remove(editor.email)
        user.auth_ids.append(form.email.data)
        editor.email = form.email.data

      if form.password.data:
        user.password = security.generate_password_hash(form.password.data,
                                                        length=12)

      editor.put()
      user.put()

      # Force reload of profile object
      Profile.get(editor.key())
      self.session.add_flash(messages.EDITOR_UPDATE_SUCCESS)

      return self.redirect_to('editors.list')

    return self.render_to_response('editors/form.haml', {'form': form})
