# Project: TIC-TAC-TOE Game - Sara Vagnarelli

## Set-Up Instructions:
-----------------------------------
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting your local server's address (by default localhost:8080.)
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.

## Files Included:

-----------------------------------
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity definitions and their helpful functions.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

## Game Description:

-----------------------------------
Tic-tac-toe noughts and crosses or Xs and Os is a paper-and-pencil game for two players, X and O, who take turns marking the spaces in a 3×3 grid. The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row wins the game. [Wikipedia](https://en.wikipedia.org/wiki/Tic-tac-toe)

The goal of Tic Tac Toe is to be the first player to get three in a row on a 3x3 grid, or four in a row in a 4x4 grid.
X always goes first.

Players alternate placing Xs and Os on the board until either (a) one player has three in a row, horizontally, vertically or diagonally; or (b) all nine squares are filled.
If a player is able to draw three Xs or three Os in a row, that player wins.
If all nine squares are filled and neither player has three in a row, the game is a draw.

Tic Tac Toe can be also be played on a 5x5 grid with each player trying to get five in a row.
The game can also be played on larger grids, such as 10x10 or even 20x20. For any grid of 6x6 or larger, I recommend sticking to a goal of getting five in a row. 

## API Game Description:
-----------------------------------

### Endpoints Included:
 
- **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will raise a ConflictException if a User with that user_name already exists.

- **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: userX, userY
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game.

- **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

- **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, user_name, move
    - Returns: GameForm with new game state.
    - Description: The games checks the player who has to move,then verifies if the move is allowed, checking if the cell is outside the board or if it is already assigned. In this way if the checks pass it signes the board and adds the move to the history. Last but not the least, it checks if the game has a winner.

- **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

- **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

- **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: user_name, email
    - Returns: GameForms
    - Description: Get all the Users with active games.

- **cancel_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage
    - Description: A user can delete his active game but only if it is still in progress.

- **get_user_rankings**
    - Path: 'user/ranking'
    - Method: GET
    - Parameters: None
    - Returns: UserForms sorted by points.
    - Description: Get all players ranked by points.

- **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage
    - Description: Get the history of a game.
    
### Models Included:
 
- **User**
    - Stores unique user_name and (optional) email address.

- **Game**
    - Stores unique game states. Associated with User models via KeyProperties
    userX and userO.

- **Score**
    - Records completed games. Associated with Users model via KeyProperty.

## Forms Included:
 
- **GameForm**
    - Representation of a Game's state (urlsafe_key, board, sizeBoard,
    userX, userO, turnOf, boolCompleted, winner, draw).
- **GameForms**
    - Multiple GameForm container.
- **NewGameForm**
    - Used to create a new game (userX, userO)
- **MakeMoveForm**
    - Inbound make move form (user_name, move).
- **ScoreForm**
    - Representation of a completed game's Score.
- **ScoreForms**
    - Multiple ScoreForm container.
- **UserForm**
    - Representation of a User.
- **UserForms**
    - Multiple UserForm Container.
- **StringMessage**
    - General purpose String container.


### Score-Keeping
-----------------------------------

* 3  Points for a Win
* 1  Points for a Tie


### Citations
-----------------------------------
Udacity forums and StackOverflow forums.
