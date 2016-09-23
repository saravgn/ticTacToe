# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import logging
import endpoints
from protorpc import remote, messages
from models import User, Game, Score, GameForm, GameForms, NewGameForm, MakeMoveForm, ScoreForm, ScoreForms, StringMessage, UserForm, UserForms
from utils import get_by_urlsafe, lookForWin, boolFullCurrentBoard
from google.appengine.api import memcache, mail
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
# ResourceContainer is used for Querystring parameters
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))


@endpoints.api(name='tic_tac_toe', version='v1')
class gameAPI(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    # returns all players ranked by performance.
    # The results should include each Player's name and the 'performance'
    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all Users ranked by points"""
        users = User.query().fetch()
        users = sorted(users, key=lambda x: x.score,
                       reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""

        playerO = User.query(User.name == request.playerO).get()
        playerX = User.query(User.name == request.playerX).get()

        # Check if playerX exist
        if not playerX:
            raise endpoints.NotFoundException(
                'A User with %s name does not exist!' % playerX)
        # Check if playerO exist
        if not playerO:
            raise endpoints.NotFoundException(
                'A User with %s name does not exist!' % playerO)
        game = Game.new_game(playerX.key, playerO.key)
        return game.to_form()

    # This endpoint returns all of a User's active games.
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(ndb.OR(Game.playerX == user.key,
                                  Game.playerO == user.key))
        games = games.filter(Game.game_over == False)
        return GameForms(items=[game.to_form() for game in games])

    # This endpoint allows users to cancel a game in progress.
    # It deletes the Game model itself
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.key.delete()
            return StringMessage(message='Game with key: {} deleted.'.
                                 format(request.urlsafe_game_key))
        elif game and game.game_over:
            raise endpoints.BadRequestException('Game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        if game.game_over:
            raise endpoints.NotFoundException('Game already over')

        user = User.query(User.name == request.user_name).get()
        if user.key != game.hasToMove:
            raise endpoints.BadRequestException('It\'s not your turn!')
        x = True if user.key == game.playerX else False

        move = request.move
        # board_size = 3
        # if move < 0 or move > 8:
        if move not in range(9):
            raise endpoints.BadRequestException('Invalid move! Must be between'
                                                '0 and %s ' % 8)
        if game.board[move] != '':
            raise endpoints.BadRequestException('Invalid move!')

        game.board[move] = 'X' if x else 'O'
        game.historyMoves.append(('X' if x else 'O', move))
        game.hasToMove = game.playerO if x else game.playerX

        # Is there a Winner?
        winner = lookForWin(game.board, 3)
        if winner:
            game.end_game(user.key)
            game.historyMoves.append(('game_over-winner:', winner))
        else:
            # Is the board full?
            boolBoardFull = boolFullCurrentBoard(game.board)
            if boolBoardFull:
                # End game tied
                game.end_game()

        game.put()
        return game.to_form()

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.historyMoves))

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.query(ndb.OR(Score.playerX == user.key,
                                    Score.playerO == user.key))
        return ScoreForms(items=[score.to_form() for score in scores])

api = endpoints.api_server([gameAPI])
