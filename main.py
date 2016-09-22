"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""

# !/usr/bin/env python
import logging
import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from models import User, Game
from api import gameAPI
from utils import get_by_urlsafe


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Reminder to users with incomplete games"""
        users = User.query(User.email is not None)
        for user in users:
            games = Game.query(ndb.OR(Game.playerX == user.key,
                                      Game.playerO == user.key)). \
                                      filter(Game.game_over is False)
            if games.count() > 0:
                subject = 'Reminder!'
                body = 'Hello {}, we advice you about the {} games, which are still in progress. The projects are: {}'. \  # noqa
                format(user.name, games.count(),  # noqa
                        ', '.join(game.key.urlsafe() for game in games))  # noqa
                logging.debug(body)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.
                               format(app_identity.get_application_id()),
                               user.email,
                               subject,
                               body)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)
