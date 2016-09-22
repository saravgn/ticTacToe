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
        users = User.query(User.email != None)
        for user in users:
            games = Game.query(ndb.OR(Game.playerX == user.key,
                                      Game.playerO == user.key)). \
                            filter(Game.game_over == False)
            if games.count() > 0:
                subject = 'This is a reminder!'
                body = 'Hello {}, this email is for advice you about the '\
                       'games that are in progress. ' \
                       'You have {} games incompleted.' \
                       'The games keys are: {}'.format(user.name, games.count(),
                                                  ', '.join(game.key.urlsafe() for game in games))
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
