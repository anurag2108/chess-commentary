'''
Responsible for user-input and showing the current game state.
'''

import pygame as p
import chess_engine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
Images = {}

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


#Main code, to handle input and update the graphics.

def main():

    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chess_engine.GameState()

    loadImages()
    running = True
    sqSelected = () #keep track of clicks of the user.
    playerClicks = [] #

    validMoves = gs.getValidMoves()
    moveMade = False

    movesMade = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE

                if sqSelected == (row,col):
                    sqSelected = () #unselect
                    playerClicks = []
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected)

                #Was the second click by the user?
                if(len(playerClicks)==2):
                    move = chess_engine.Move(playerClicks[0], playerClicks[1], gs.board) 
                    moveMade = move.getChessNotation()
                    #Adjust the board with the moveMade to stockfish.
                    #Ask stockfish to suggest moves.
                    #Pass those moves to LLM for commentary.
                    movesMade.append(moveMade)
                    if(move in validMoves):
                        gs.makeMove(move)
                        moveMade=True
                        sqSelected = ()
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade=True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()

if __name__ == "__main__":
    main()
    

