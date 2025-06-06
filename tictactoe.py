from tkinter import *
import random

root = Tk()
root.geometry("330x550")
root.title("Tic Tac Toe")

root.resizable(False,False) # Disable resizing the window
root.configure(bg = "black") # Set background color of the window

Frame1 = Frame(root)
Frame1.pack()
titleLabel = Label(Frame1,text ="Tic Tac Toe",font = ("Arial",26),bg = "yellow", width = 16)
titleLabel.grid(row = 0,column = 0)

gameChoiceFrame = Frame(root,bg = "grey")
gameChoiceFrame.pack() # Add some vertical padding

frame2 = Frame(root)
frame2.pack()

canvas = Canvas(frame2, width=300, height=300, bg='black', highlightthickness=0)
canvas.place(x=0, y=0)

def getCellCentre(index):
    """
    Returns the center coordinates of a cell in a 3x3 grid based on the index.
    The index is 1-based (1 to 9).
    """
    row = (index - 1) // 3
    col = (index - 1) % 3
    x = col * 100 + 50  # Center x-coordinate
    y = row * 100 + 50  # Center y-coordinate
    return x, y

def animateWinningLine(start,end):
    """
    Animates a winning line from the start point to the end point using incremental drawing.

    Parameters:
    start (tuple): A tuple (x, y) representing the starting coordinates of the line.
    end (tuple): A tuple (x, y) representing the ending coordinates of the line.

    The function creates a smooth animation by gradually updating the line's end position
    over a series of steps using the Tkinter `after()` method for timed callbacks.
    """
    steps = 20
    xPos = (end[0] - start[0]) / steps
    yPos = (end[1] - start[1]) / steps
    line = canvas.create_line(start[0], start[1], start[0], start[1], fill='pink', width=5)
    def draw(step):
        if step > steps:
            return
        canvas.coords(line, start[0], start[1], start[0] + xPos * step, start[1] + yPos * step)
        root.after(20, draw, step + 1)
    draw(0)
# 2D board 3 X 3

board = {
#   1     2     3
    1: "",2: "",3: "", # 1
    4: "",5: "",6: "", # 2
    7: "",8: "",9: ""  # 3
         }

turn = "X"
gameEnd = False
winningLabel = None  # To hold the label widget for win/draw messages
gameMode = "singleplayer" # Default game mode

def toMultiplayer():
    """
    Sets the game mode to multiplayer and updates the button backgrounds
    to reflect the current selection.

    This function changes the global `gameMode` variable to "multiplayer",
    highlights the multiplayer button in grey, and resets the single player
    button's background to red.
    """
    global gameMode
    gameMode = "multiplayer"
    multiPlayer["bg"] = "grey"
    singlePlayer["bg"] = "red"

def toSinglePlayer():
    """
    Sets the game mode to single player and updates the button backgrounds
    to reflect the current selection.

    This function changes the global `gameMode` variable to "singleplayer",
    highlights the single player button in grey, and resets the multiplayer
    button's background to red.
    """
    global gameMode
    gameMode = "singleplayer"
    singlePlayer["bg"] = "grey"
    multiPlayer["bg"] = "red"

def updateBoard():
    """
    Updates the button texts and colors on the GUI
    based on the current state of the board dictionary.

    For each key (1 to 9) in the board:
    - Calculates the corresponding row and column in the 3x3 grid.
    - Sets the button text to the board value ("X", "O", or empty).
    - Changes the text color based on the player:
        - Red for "X"
        - Blue for "O"
        - Black if the cell is empty
    """
    for key in board.keys():
        row = (key - 1) // 3
        col = (key - 1) % 3
        buttons[row][col]["text"] = board[key]
        if board[key] == "X":
            buttons[row][col]["fg"] = "red"
        elif board[key] == "O":
            buttons[row][col]["fg"] = "blue"
        else:
            buttons[row][col]["fg"] = "black"  # Reset color if empty

def checkForWin(player):
    """
    Checks if the given player has achieved a winning combination on the board.

    Parameters:
    player (str): The symbol of the player to check for a win ("X" or "O").

    Returns:
    tuple or None: Returns a tuple (start_cell, end_cell) representing the start and end 
    positions of the winning line if a win is detected. Returns None if no winning combination is found.

    The function checks all possible winning combinations:
    - Horizontal rows
    - Vertical columns
    - Two diagonals
    """
    winningCombinations = [
        (1,2,3), (4,5,6), (7,8,9), # Rows
        (1,4,7), (2,5,8), (3,6,9), # Columns
        (1,5,9), (3,5,7)           # Diagonals
    ]
    for a,b,c in winningCombinations:
        if board[a] == board[b] == board[c] == player:
            return (a, c)  # Return start and end cells
    return None

def checkForDraw():
    """
    Checks whether the game has resulted in a draw.

    A draw is identified if all cells on the board are filled and no player has won.
    
    Returns:
    - False: If there is at least one empty cell (the game is still ongoing).
    - True: If all cells are filled (potential draw, assuming no win has occurred).
    """
    for a in board.keys():
        if board[a] == "":
            return False
    return True

def clearWinningLabel():
    """
    Clears the winning or draw label from the GUI.

    If the `winningLabel` exists on the screen, this function removes it
    and resets the reference to None.
    """
    global winningLabel
    if winningLabel is not None:
        winningLabel.destroy()
        winningLabel = None

def restartGame():
    """
    Resets the game to its initial state.

    This function performs the following actions:
    - Resets the gameEnd flag to False and sets the turn back to "X".
    - Clears the winning/draw label from the GUI (if it exists).
    - Empties all button texts and sets their text color to black.
    - Resets all entries in the internal board dictionary to empty strings.
    - Updates the title label to display "Tic Tac Toe" at the top of the window.

    Typically triggered when the player clicks a 'Restart' button to begin a new game.
    """
    global gameEnd, turn
    gameEnd = False
    turn = "X" # Reset turn to X
    clearWinningLabel()
    for button in buttonsList:
        button["text"] = ""
        button["fg"] = "black"
    for a in board.keys():
        board[a] = ""
    # Recreate the title label cleanly
    titleLabel.config(text="Tic Tac Toe")

def minMax(board, isMax, difficulty):
    """
    Implements the Minimax algorithm with adjustable difficulty 
    to evaluate the best possible move for the current board state.

    Parameters:
    - board (dict): The current state of the Tic Tac Toe board with keys 1–9.
    - isMax (bool): 
        True if it's the maximizing player's turn (computer 'O').
        False if it's the minimizing player's turn (human 'X').
    - difficulty (float): A value between 0 and 1 representing the computer's 
      likelihood to choose the optimal move (higher = smarter).

    Returns:
    - int: The best score the current player can achieve from this board state:
        +1 for a win by 'O' (computer),
        -1 for a win by 'X' (human),
         0 for a draw.

    This recursive function simulates all possible future moves for both 
    players and evaluates each scenario. It uses randomness to vary the 
    AI’s behavior based on the difficulty level—occasionally making sub-optimal 
    moves to mimic human-like play at lower difficulties.
    """
    if checkForWin("O"):
        return 1
    elif checkForWin("X"):
        return -1
    elif checkForDraw():
        return 0

    if isMax:
        scores = []
        for key in board:
            if board[key] == "":
                board[key] = "O"
                score = minMax(board, False, difficulty)
                board[key] = ""
                scores.append((score, key))
        scores.sort(reverse=True)
        if random.random() < difficulty:
            return scores[0][0]
        else:
            return random.choice(scores[1:])[0] if len(scores) > 1 else scores[0][0]
    else:
        scores = []
        for key in board:
            if board[key] == "":
                board[key] = "X"
                score = minMax(board, True, difficulty)
                board[key] = ""
                scores.append((score, key))
        scores.sort()
        if random.random() < difficulty:
            return scores[0][0]
        else:
            return random.choice(scores[1:])[0] if len(scores) > 1 else scores[0][0]        

def playComputer():
    """
    Determines and executes the best move for the computer player ('O') 
    using the Minimax algorithm with variable difficulty.

    Process:
    - Skips execution if the game has already ended.
    - Generates a difficulty factor between 0.6 and 1.0 (higher = smarter).
    - Iterates through all empty cells on the board:
        - Simulates placing 'O' in each cell.
        - Uses Minimax to score the outcome.
        - Tracks the move with the highest score.
    - Makes the best move by placing 'O' on the selected cell.
    - Updates the GUI board accordingly.
    - Checks if this move results in a win:
        - If yes: displays a "O wins the game" label and animates the winning line.
    - If not a win, it checks for a draw and updates the label if the game is drawn.

    This function ensures the computer plays optimally (or near-optimally) 
    based on the difficulty level, providing a challenge to the player.
    """
    global gameEnd, winningLabel
    if gameEnd:
        return

    difficulty = random.uniform(0.6, 1.0) # Random difficulty factor between 0.6 and 1.0
    bestScore = -100
    bestMove = None

    for key in board:
        if board[key] == "":
            board[key] = "O"
            score = minMax(board, False, difficulty)
            board[key] = ""
            if score > bestScore:
                bestScore = score
                bestMove = key

    if bestMove is not None:
        board[bestMove] = "O"
        updateBoard()
        winCombo = checkForWin("O")
        if winCombo:
            clearWinningLabel()
            winningLabel = Label(Frame1, text="O wins the game", bg="yellow", font=("Arial", 26), width=16)
            winningLabel.grid(row=0, column=0, columnspan=3)
            start, end = getCellCentre(winCombo[0]), getCellCentre(winCombo[1])
            animateWinningLine(start, end)
            gameEnd = True
        elif checkForDraw():
            clearWinningLabel()
            winningLabel = Label(Frame1, text="Game Draw!", bg="yellow", font=("Arial", 26), width=16)
            winningLabel.grid(row=0, column=0, columnspan=3)
            gameEnd = True

def play(event):
    """
    Handles the player's move when a grid button is clicked.

    Function Flow:
    1. Ignores input if the game has already ended.
    2. Identifies which button was clicked based on the event.
    3. Converts the button's position into a corresponding key (1–9) in the board dictionary.
    4. If the button is empty:
        - Places the current player's symbol ("X" or "O") on it.
        - Updates the internal game board state.
    5. Checks if the current player has achieved a winning combination:
        - If yes: displays a winning message and animates the winning line.
    6. If no win, checks for a draw:
        - If yes: displays a "Game Draw!" message.
    7. If the game is still ongoing:
        - In multiplayer mode: switches the turn to the other player.
        - In singleplayer mode: computer plays automatically using `playComputer()` 
          after the human player ('X') makes a move.

    Parameters:
    - event: Tkinter event object passed from the button click event.
    """
    global turn, gameEnd, winningLabel

    if gameEnd:
        return

    button = event.widget
    index = None

    for a in range(3):
        for b in range(3):
            if buttons[a][b] == button:
                index = a * 3 + b + 1
                break
        if index is not None:
            break

    if board[index] == "":
        board[index] = turn
        updateBoard()

        winCombo = checkForWin(turn)
        if winCombo:
            clearWinningLabel()
            winningLabel = Label(Frame1, text=f"{turn} wins the game", bg="yellow", font=("Arial", 26), width=16)
            winningLabel.grid(row=0, column=0, columnspan=3)
            start, end = getCellCentre(winCombo[0]), getCellCentre(winCombo[1])
            animateWinningLine(start, end)
            gameEnd = True
        elif checkForDraw():
            clearWinningLabel()
            winningLabel = Label(Frame1, text="Game Draw!", bg="yellow", font=("Arial", 26), width=16)
            winningLabel.grid(row=0, column=0, columnspan=3)
            gameEnd = True
        else:
            if gameMode == "multiplayer":
                turn = "O" if turn == "X" else "X"
            else:
                # In singleplayer, if it's player's turn (X), computer (O) plays next
                if turn == "X":
                    turn = "O"
                    playComputer()
                    turn = "X"

# -----------------------GUI part----------------------------------

"""
Sets up the game mode selection buttons, the Tic Tac Toe board grid, and the restart button.

Details:
- Creates two mode selection buttons ("Single player" and "Multi player") inside 'gameChoiceFrame'.
  * Both buttons are styled with blue background and white text.
  * The buttons are positioned side by side with padding and sticky alignment.
  * Each button is linked to its respective command function ('toSinglePlayer' and 'toMultiplayer') 
    to switch game modes and update button colors.

- Creates a 3x3 grid of buttons inside 'frame2' representing the Tic Tac Toe board.
  * Each button is styled with green background, large font size, and a raised border.
  * Buttons are arranged using grid layout by rows and columns.
  * Each button is bound to the 'play' function to handle player moves on click.
  * The buttons are stored in a 2D list called 'buttons' for easy access by row and column.

- Creates a "Restart" button below the grid in 'frame2'.
  * The button is styled with a red background and white text.
  * It spans all three columns and triggers 'restartGame' when clicked.

- Flattens the 2D 'buttons' list into a single list 'buttonsList' for easy iteration and manipulation.
"""

singlePlayer = Button(gameChoiceFrame, text="Single player", width=13, height=1,font=("Arial", 15), bg="blue", fg="white", relief=RAISED, borderwidth=3)
singlePlayer.grid(row=3, column=0, padx=5, pady=3, sticky="W")

multiPlayer = Button(gameChoiceFrame, text="Multi player", width=13, height=1,font=("Arial", 15), bg="blue", fg="white", relief=RAISED, borderwidth=3)
multiPlayer.grid(row=3, column=1, padx=5, pady=3, sticky="E")
singlePlayer.config(command=toSinglePlayer)
multiPlayer.config(command=toMultiplayer)

# Tic Tac Toe board

# 2D grid 3 X 3

buttons = []

for row in range(3):
    rowButtons = []
    for column in range(3):
        btn = Button(frame2, 
                     text = "", 
                     width = 4, 
                     height = 2, 
                     font = ("Arial", 30), 
                     bg = "green", 
                     relief = RAISED, 
                     borderwidth = 5)
        btn.grid(row = row, column = column)
        btn.bind("<Button-1>", play)
        rowButtons.append(btn)
    buttons.append(rowButtons)

restartButton = Button(frame2, text = "Restart", width = 19, height = 1, font = ("Arial",20), bg = "red", fg = "white", relief = RAISED, borderwidth = 3, command = restartGame)
restartButton.grid(row = 3, column = 0, columnspan = 3)

buttonsList = [btn for row in buttons for btn in row]

root.mainloop()
