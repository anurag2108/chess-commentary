'''
Responsible for user-input and showing the current game state.
'''

import pygame as p
import chess_engine  # Your module for game state and move generation
import chess
import chess.engine
import pyttsx3
import requests
import ollama

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
Images = {}

# ----- TTS Setup -----
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Adjust speech rate if desired

# ----- Stockfish Setup -----
stockfish_path = "/stockfish-macos-x86-64"  # Update with your Stockfish binary path
sf_engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

# ----- Global Move History (for context in commentary) -----
white_moves_history = []
black_moves_history = []

'''
Initialize a dictionary of Images, called once.
'''

def loadImages():
    pieces = ['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bQ','bK']
    for piece in pieces:
        Images[piece] = p.transform.scale(p.image.load("myenv/images/"+piece+".png"),(SQ_SIZE,SQ_SIZE))


#All Graphics
def drawGameState(screen,gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)

#Draw the squares on the board.
def drawBoard(screen):
    colors = [p.Color("white"),p.Color("grey")]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

            

#Draw the pieces on the board.
def drawPieces(screen, board):

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]

            if(piece!="--"):
                screen.blit(Images[piece],p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))


def get_best_lines(current_board, engine, num_lines=3, line_length=5):
    """
    For the given board (a python-chess Board object), generate 'num_lines'
    best move sequences of length 'line_length' by simulating moves using Stockfish.
    Returns a list of dictionaries: {'line': [list of moves in UCI], 'evaluation': score}
    """
    lines = []
    for _ in range(num_lines):
        temp_board = current_board.copy()
        line_moves = []
        for i in range(line_length):
            result = engine.play(temp_board, chess.engine.Limit(depth=16))
            line_moves.append(result.move.uci())
            temp_board.push(result.move)
        # Get evaluation of final position (score from White's perspective)
        info = engine.analyse(temp_board, chess.engine.Limit(depth=16))
        score = info["score"].white().score(mate_score=10000)
        lines.append({"line": line_moves, "evaluation": score})
    return lines

def get_current_evaluation(current_board, engine):
    info = engine.analyse(current_board, chess.engine.Limit(depth=16))
    score = info["score"].white().score(mate_score=10000)
    return score

def generate_deepseek_prompt(move_played, white_history, black_history, best_lines, current_eval):
    """
    Build a prompt string for DeepSeek using:
      - move_played: the notation for the move just made.
      - white_history, black_history: comma-separated strings of moves so far.
      - best_lines: a list of dicts with 'line' and 'evaluation'
      - current_eval: current evaluation score.
    """
    prompt = f""" **Game Context**: White's moves so far: {', '.join(white_history) if white_history else 'None'} Black's moves so far: {', '.join(black_history) if black_history else 'None'}

    **Latest Move**:
    Move played: {move_played}

    **Current Board Evaluation**:
    Evaluation (in centipawns from White's perspective): {current_eval}

    **Stockfish Analysis**:
    Here are the top suggested lines (each with 5 moves) from Stockfish:
    """
    for i, line in enumerate(best_lines, start=1):
        moves_str = ' '.join(line['line'])
        prompt += f"\nLine {i}: {moves_str}  (Evaluation: {line['evaluation']})"
    
    prompt += """

    **Your Task**:
    As a world-class chess commentator, provide exciting, suspenseful, and dramatic commentary on the move just played and the board situation. Highlight if the move is a blunder, an inaccuracy, or a brilliant tactical stroke. Build tension and use storytelling to make the audience sit on the edge of their seats. Include voice modulation hints (e.g., rising tone, dramatic pause) in your commentary.
    """

    return prompt

def get_deepseek_commentary(prompt):
    """
    Use Ollama to chat with the DeepSeek model for commentary.
    """
    response = ollama.chat(
        model="deepseek-r1",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return response["message"]["content"]

def speak_commentary(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

#Main code, to handle input and update the graphics.

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chess_engine.GameState()  # Your game state (manages board, moves, etc.)
    
    # Also create a python-chess Board for analysis with Stockfish:
    analysis_board = chess.Board()  # We'll update this as moves are made
    
    loadImages()
    running = True
    sqSelected = ()  # Track user clicks
    playerClicks = []  # Record clicks
    validMoves = gs.getValidMoves()
    moveMadeFlag = False
    
    # Global move history (for commentary context) is maintained in white_moves_history and black_moves_history
    movesMade = []
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if sqSelected == (row, col):
                    sqSelected = ()  # Unselect
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                
                # When two clicks are made, attempt to form a move
                if len(playerClicks) == 2:
                    move = chess_engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    moveNotation = move.getChessNotation()
                    print("Move made:", moveNotation)
                    
                    movesMade.append(moveNotation)
                    # Update move history: determine whose move it was based on current move count
                    if gs.whiteToMove:  # If white is moving now, then after move, add to white's history
                        white_moves_history.append(moveNotation)
                    else:
                        black_moves_history.append(moveNotation)
                    
                    if move in validMoves:
                        gs.makeMove(move)  # Update game state via your engine
                        moveMadeFlag = True
                        sqSelected = ()
                        playerClicks = []
                        
                        # Also update the analysis_board (python-chess board) with this move:
                        try:
                            # Assume moveNotation is in UCI format; if not, you may need to convert it.
                            # Here, we assume our getChessNotation returns UCI-like string for analysis.
                            uci_move = chess.Move.from_uci(moveNotation)
                        except Exception as ex:
                            # If not, try constructing a UCI move manually using rank file conversion
                            # For now, we assume it works.
                            uci_move = None
                        if uci_move and uci_move in analysis_board.legal_moves:
                            analysis_board.push(uci_move)
                        else:
                            # Alternatively, if conversion fails, you can update analysis_board via your gs board.
                            # For now, we assume the move is applied to analysis_board as well.
                            pass
                        
                        # ----- Stockfish Analysis ----- #
                        # Get three best move sequences (each 5 moves) and current evaluation
                        best_lines = get_best_lines(analysis_board, sf_engine, num_lines=3, line_length=5)
                        current_eval = get_current_evaluation(analysis_board, sf_engine)
                        
                        # ----- Build the DeepSeek Prompt ----- #
                        prompt = generate_deepseek_prompt(moveNotation, white_moves_history, black_moves_history, best_lines, current_eval)
                        print("DeepSeek Prompt:\n", prompt)
                        
                        # ----- Get Commentary from DeepSeek ----- #
                        commentary = get_deepseek_commentary(prompt)
                        print("DeepSeek Commentary:\n", commentary)
                        
                        # ----- Use TTS to Speak the Commentary ----- #
                        speak_commentary(commentary)
                    else:
                        playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    if analysis_board.move_stack:  # Undo move in analysis_board as well
                        analysis_board.pop()
                    moveMadeFlag = True

        if moveMadeFlag:
            validMoves = gs.getValidMoves()
            moveMadeFlag = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

    sf_engine.quit()

if __name__ == "__main__":
    main()