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

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def getChessNotation(self):
        #Can Create real chess notation from here.
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

