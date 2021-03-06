import wsgiref.handlers
import hashlib, time

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required

from main import Account, Notification, Channel, API_HOST, API_VERSION

class HomeHandler(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        account = Account.all().filter('user =', user).get()
        if not account:
            account = Account()
            account.set_hash_and_key()
            account.put()
        self.redirect('/dashboard/history')

class SettingsHandler(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        account = Account.all().filter('user =', user).get()
        api_host = API_HOST
        api_version = API_VERSION
        pending_channels = Channel.get_all_by_target(account).filter('status =', 'pending')
        self.response.out.write(template.render('templates/dashboard_settings.html', locals()))
    
    def post(self):
        user = users.get_current_user()
        account = Account.all().filter('user =', user).get()
        if self.request.get('source_enabled', None):
            account.source_enabled = True
            account.source_name = self.request.get('source_name', None)
            account.source_icon = self.request.get('source_icon', None)
        else:
            account.source_enabled = False
        account.put()
        self.redirect('/dashboard/settings')

class HistoryHandler(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        account = Account.all().filter('user =', user).get()
        api_host = API_HOST
        api_version = API_VERSION
        pending_channels = Channel.get_all_by_target(account).filter('status =', 'pending')
        notifications = Notification.all().filter('target =', account).order('-created').fetch(1000)
        self.response.out.write(template.render('templates/dashboard_history.html', locals()))

class SourcesHandler(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        account = Account.get_by_user(user)
        pending_channels = Channel.get_all_by_target(account).filter('status =', 'pending')
        enabled_channels = Channel.get_all_by_target(account).filter('status =', 'enabled')
        self.response.out.write(template.render('templates/dashboard_sources.html', locals()))
    
    def post(self):
        user = users.get_current_user()
        account = Account.get_by_user(user)
        action = self.request.get('action')
        if action == 'approve':
            source = Account.get_by_hash(self.request.get('source'))
            channel = Channel.get_by_source_and_target(source, account)
            channel.status = 'enabled'
            channel.put()
        if action == 'disable':
            source = Account.get_by_hash(self.request.get('source'))
            channel = Channel.get_by_source_and_target(source, account)
            channel.status = 'disabled'
        self.redirect('/dashboard/sources')

class NotifiersHandler(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        account = Account.get_by_user(user)
        logout_url = users.create_logout_url('/')
        pending_channels = Channel.get_all_by_target(account).filter('status =', 'pending')
        self.response.out.write(template.render('templates/dashboard_notifiers.html', locals()))

def main():
    application = webapp.WSGIApplication([
        ('/dashboard', HomeHandler), 
        ('/dashboard/settings', SettingsHandler),
        ('/dashboard/history', HistoryHandler),
        ('/dashboard/sources', SourcesHandler),
        ('/dashboard/notifiers', NotifiersHandler),
        ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()