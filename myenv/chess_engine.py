'''
Storing the information about the current state of the chess game, 

1. it will also be responsible to determine set of valid moves at the current state.
2. Undo/Make moves from the current position.
'''


class GameState():
    def __init__(self):
        #Pretty obvious notation. 
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp','bp','bp','bp','bp','bp','bp','bp'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']
        ]
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self,move):
        self.board[move.startRow][move.startCol] = "--" 
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove #switch move

    def undoMove(self):
        if(len(self.moveLog)!=0):
            lastmove = self.moveLog.pop()
            self.board[lastmove.startRow][lastmove.startCol] = lastmove.pieceMoved
            self.board[lastmove.endRow][lastmove.endCol] = lastmove.pieceCaptured
            self.whiteToMove = not self.whiteToMove
    
    def getValidMoves(self):
        return self.getAllPossibleMoves()

    def getAllPossibleMoves(self):
        moves = []

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if((turn == "w" and self.whiteToMove) or (turn=="b" and not self.whiteToMove)):
                    piece = self.board[r][c][1]
                    if piece == "p":
                        self.getPawnMoves(r,c,moves)
                    elif piece == "R":
                        self.getRookMoves(r,c,moves)
                    elif piece == "N":
                        self.getKnightMoves(r,c,moves)
                    elif piece == "B":
                        self.getBishopMoves(r,c,moves)
                    elif piece == "Q":
                        self.getQueenMoves(r,c,moves)
                    elif(piece == "K"):
                        self.getKingMoves(r,c,moves)
        
        return moves
    
    #get all pawn moves
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:
            #Pawn can only move 2 moves in the initial square hence, hard coded to r==6.
            if r-1>=0 and self.board[r-1][c] == '--': #1 move advance
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == '--': #2 move advance
                    moves.append(Move((r,c),(r-2,c),self.board))
            
            #captures
            if c-1>=0 and r-1>=0: #to the left
                if(self.board[r-1][c-1][0]=='b'):
                    moves.append(Move((r,c),(r-1,c-1),self.board))

            if c+1<=7 and r-1>=0: #to the right
                if(self.board[r-1][c+1][0]=='b'):
                    moves.append(Move((r,c),(r-1,c+1),self.board))

        else:
            if r+1<=7 and self.board[r+1][c] == "--": #1 move advance black
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == '--': #2 move advance black
                    moves.append(Move((r,c),(r+2,c),self.board))
            
            #captures
            if c-1>=0 and r+1<=7:
                if(self.board[r+1][c-1][0]=='w'): #right black capture
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                
            if c+1<=7 and r+1<=7:
                if(self.board[r+1][c+1][0]=='w'): #left black capture
                    moves.append(Move((r,c),(r+1,c+1),self.board))

        #Add pawn promotions and en-passant
            
    #get all rook moves
    def getRookMoves(self,r,c,moves):
        directions = [(-1,0),(1,0),(0,1),(0,-1)]
        enemycolor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i

                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemycolor: #cant go further once enemey piece found
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else: #friendly piece invalid after
                        break
                else:
                    break
            
    #get all Knight moves
    def getKnightMoves(self,r,c,moves):
        directions = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        allycolor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r+d[0]
            endCol = c+d[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allycolor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    #get all Bishop moves
    def getBishopMoves(self,r,c,moves):
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)] # Exactly same with rook moves, with different directions.
        enemycolor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i

                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemycolor: #cant go further once enemey piece found
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else: #friendly piece invalid after
                        break
                else:
                    break

    #get all Queen moves
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    #get all rook moves
    def getKingMoves(self,r,c,moves):
        directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        allycolor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r+d[0]
            endCol = c+d[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allycolor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))

class Move():

    ranksToRows = {"1":7, "2":6 , "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}

    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}

    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self,startSq,endSq,board):

        self.startRow = startSq[0]
        self.startCol = startSq[1]

        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.moveId = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

    
    '''
    Overriding the equal method
    '''
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveId == other.moveId
        return False

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def getChessNotation(self):
        #Can Create real chess notation from here.
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

