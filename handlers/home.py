from handlers import base
from library.auth import login_not_required


class HomeHandler(base.BaseHandler):

  @login_not_required
  def home(self):
    if self.get_current_profile():
      return self.private_home()
    else:
      return self.public_home()

  @login_not_required
  def public_home(self):
    return self.render_to_response('oneStop.html', use_cache=False)
    # return self.render_to_response('corporate/home.haml', use_cache=True)


  def private_home(self):
    if self.get_current_profile().is_admin:
      return self.render_to_response('order.html', use_cache=False)
      # return self.render_to_response('corporate/manager_dashboard.haml')


    return self.render_to_response('order.html', use_cache=False)
