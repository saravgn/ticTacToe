"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    ties = ndb.IntegerProperty(default=0)
    los = ndb.IntegerProperty(default=0)
    matches_played = ndb.IntegerProperty(default=0)

    @property
    def score(self):
        """User points"""
        return (self.wins-self.los)/total_matches_played

    @classmethod
    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins,
                        ties=self.ties,
                        los=self.los,
                        matches_played=self.matches_played,
                        score=self.score)

    def updateMatchesPlayed(self):
        """Updates the value of the matches played by the user"""
        self.matches_played += 1
        self.put()

    def addWin(self):
        """Add a win"""
        self.wins += 1
        self.put()

    def addTie(self):
        """Add a tie"""
        self.ties += 1
        self.put()

    def addLoss(self):
        """Add a loss """
        self.los += 1
        self.put()


class Game(ndb.Model):
    """Game object"""
    board = ndb.PickleProperty(required=True)
    boardDimension = ndb.IntegerProperty(required=True, default=3)
    hasToMove = ndb.KeyProperty(required=True)
    playerX = ndb.KeyProperty(required=True, kind='User')
    playerO = ndb.KeyProperty(required=True, kind='User')
    historyMoves = ndb.PickleProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()
    tie = ndb.BooleanProperty(default=False)

    @classmethod
    # def new_game(cls, user, min, max, attempts):
    def new_game(cls, playerX, playerO, boardDimension=3):
        """Creates and returns a new game"""
        game = Game(playerX=playerX,
                    playerO=playerO,
                    hasToMove=playerX)

        game.board = ['' for _ in range(boardDimension*boardDimension)]
        game.historyMoves = []
        game.boardDimension = boardDimension
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        gameform = GameForm(urlsafe_key=self.key.urlsafe(),
                            board=str(self.board),
                            boardDimension=self.boardDimension,
                            playerX=self.playerX.get().name,
                            playerO=self.playerO.get().name,
                            hasToMove=self.hasToMove.get().name,
                            game_over=self.game_over)
        if self.winner:
            gameform.winner = self.winner.get().name
        if self.tie:
            gameform.tie = self.tie
        return gameform

    def end_game(self, winner=None):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""

        # update game details
        self.game_over = True
        if winner:
            self.winner = winner
        else:
            self.tie = True

        self.put()

        # Create variable result and update the user models
        if winner == self.playerX:
            # create variable result for Score entity
            result = 'playerX'
            # add a los to the loser,a win to the winner or tie
            playerO.get().add_loss()
            winner.get().add_win

        elif winner == self.playerO:
            result = 'playerO'
            playerX.get().add_loss()
            winner.get().add_win

        else:
            result = 'tie'
            self.playerX.get().add_tie()
            self.playerO.get().add_tie()

        # Add the game to the score 'board'
        score = Score(date=date.today(), playerX=self.playerX,
                      playerO=self.playerO, result=result)


class Score(ndb.Model):
    """Score object"""
    playerX = ndb.KeyProperty(required=True, kind='User')
    playerO = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    result = ndb.StringProperty(required=True)

    def to_form(self):
        return ScoreForm(date=str(self.date),
                         playerX=self.user_x.get().name,
                         playerO=self.user_o.get().name,
                         result=self.result)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    boardDimension = messages.IntegerField(3, required=True)
    playerX = messages.StringField(4, required=True)
    playerO = messages.StringField(5, required=True)
    hasToMove = messages.StringField(6, required=True)
    game_over = messages.BooleanField(7, required=True)
    winner = messages.StringField(8)
    tie = messages.BooleanField(9)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    playerX = messages.StringField(1, required=True)
    playerO = messages.StringField(2, required=True)
    boardDimension = messages.IntegerField(3)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    move = messages.IntegerField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    date = messages.StringField(1, required=True)
    playerX = messages.StringField(2, required=True)
    playerO = messages.StringField(3, required=True)
    result = messages.StringField(4)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class GameForms(messages.Message):
    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    ties = messages.IntegerField(4, required=True)
    los = messages.IntegerField(5, required=True)
    matches_played = messages.IntegerField(6, required=True)


class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)
