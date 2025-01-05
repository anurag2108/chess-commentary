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

        #check 
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.isCheck = False
        self.pins = []
        self.checks = []

        self.currentCastlingRights = CastlingRights(True,True,True,True)
        self.castleRightsLog = [CastlingRights(self.currentCastlingRights.bks, self.currentCastlingRights.bqs,
                                                self.currentCastlingRights.wqs,self.currentCastlingRights.wks)]

    def makeMove(self,move):
        
        valid_moves = self.getValidMoves()
        move_exists = False
        actual_move = None
    
        for valid_move in valid_moves:
            if (valid_move.startRow == move.startRow and 
                valid_move.startCol == move.startCol and 
                valid_move.endRow == move.endRow and 
                valid_move.endCol == move.endCol):
                move_exists = True
                actual_move = valid_move
                break
    
        if not move_exists:
            return False
        
        move = actual_move

        self.board[move.startRow][move.startCol] = "--" 
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove #switch move

        #update the kings location if moved.
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow,move.endCol)

        #print(move.isCastleMove)
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves the rook to new square
                self.board[move.endRow][move.endCol+1] = '--' #erases rook in the prev position
            
            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #moves the rook to new square
                self.board[move.endRow][move.endCol-2] = '--' #erases rook in the prev position

        #Updating castling rights whenever rook or king moves - only the first time maybe.
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastlingRights(self.currentCastlingRights.bks, self.currentCastlingRights.bqs,
                                                self.currentCastlingRights.wqs,self.currentCastlingRights.wks))
    
    def updateCastleRights(self,move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: #left Rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: #left Rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False
        
    def undoMove(self):
        if(len(self.moveLog)!=0):
            lastmove = self.moveLog.pop()
            self.board[lastmove.startRow][lastmove.startCol] = lastmove.pieceMoved
            self.board[lastmove.endRow][lastmove.endCol] = lastmove.pieceCaptured
            self.whiteToMove = not self.whiteToMove
        
            #update the kings location if moved.
            if lastmove.pieceMoved == "wK":
                self.whiteKingLocation = (lastmove.endRow,lastmove.endCol)
            elif lastmove.pieceMoved == "bK":
                self.blackKingLocation = (lastmove.endRow,lastmove.endCol)
            
            #undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1]

            #undo castle move.
            if lastmove.isCastleMove:
                if lastmove.endCol - lastmove.startCol == 2: #kingside castle move
                    self.board[lastmove.endRow][lastmove.endCol+1] = self.board[lastmove.endRow][lastmove.endCol-1] #moves the rook to new square
                    self.board[lastmove.endRow][lastmove.endCol-1] = '--' #erases rook in the prev position
            
                else: #queenside castle move
                    self.board[lastmove.endRow][lastmove.endCol-2] = self.board[lastmove.endRow][lastmove.endCol+1] #moves the rook to new square
                    self.board[lastmove.endRow][lastmove.endCol+1] = '--' #erases rook in the prev position
    
    def getValidMoves(self):
        moves = []
        self.inCheck,self.pins,self.checks = self.checkForPinsAndChecks()
        tempCastleRights = CastlingRights(self.currentCastlingRights.bks, self.currentCastlingRights.bqs,self.currentCastlingRights.wqs,self.currentCastlingRights.wks)

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves() #block check or move king, find another piece to block the check.
                check = self.checks[0]

                checkRow = check[0]
                checkCol = check[1]

                pieceChecking = self.board[checkRow][checkCol]

                validSquares = []

                if pieceChecking[1] == "N":
                    validSquares = [(checkRow,checkCol)]
                
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i, kingCol+ check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0]==checkRow and validSquare[1]==checkCol:
                            break
                
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1]!="K":
                        if not (moves[i].endRow,moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow,kingCol,moves)
        else:
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)

        self.currentCastlingRights = tempCastleRights
        return moves
    
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]

        if not self.whiteToMove:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        for j in range(len(directions)):
            possiblePin = ()
            d = directions[j]
            for i in range(1,8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i

                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1]!= 'K':
                        if possiblePin == ():
                            possiblePin = (endRow,endCol,d[0],d[1]) #First allied piece could be pinned
                        else:
                            break #Second allied piece, so no check or pin possible in the same direction
                    
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        '''
                        five possible conditions.
                        1. perpendicularly straight with a rook.
                        2. diagonally because of a bishop.
                        3. 1 square diagonally because of a pawn
                        4. any direction because of a queen
                        5. because of a king.
                        '''
                        if(0<=j<=3 and type =="R") or \
                            (4<=j<=7 and type =="B") or \
                            (i==1 and type =='p' and ((enemyColor=='w' and 6<=j<=7) or (enemyColor=="b" and 4<=j<=5))) or \
                            (type == 'Q') or (i==1 and type =="K"):
                            
                            if possiblePin == (): #no piece blocking, so check
                                inCheck = True
                                checks.append((endRow,endCol,d[0],d[1]))
                                break

                            else: #piece blocking, so pin
                                pins.append(possiblePin)
                                break
                        else: #enemy piece is not applying check
                            break

                else:
                    break

        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow,endCol,m[0],m[1]))

        return inCheck, pins, checks

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
        piecePinned = False

        pinDirection = ()

        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: #Pawn can only move 2 moves in the initial square hence, hard coded to r==6.
            if self.board[r-1][c] == '--': #1 move advance
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r,c),(r-1,c),self.board))
                    if r == 6 and self.board[r-2][c] == '--': #2 move advance
                        moves.append(Move((r,c),(r-2,c),self.board))
            
            #captures
            if c-1>=0: #to the left
                if(self.board[r-1][c-1][0]=='b'):
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r,c),(r-1,c-1),self.board))

            if c+1<=7 and r-1>=0: #to the right
                if(self.board[r-1][c+1][0]=='b'):
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r,c),(r-1,c+1),self.board))

        else:
            if self.board[r+1][c] == "--": #1 move advance black
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r,c),(r+1,c),self.board))
                    if r == 1 and self.board[r+2][c] == '--': #2 move advance black
                        moves.append(Move((r,c),(r+2,c),self.board))
            
            #captures
            if c-1>=0:
                if(self.board[r+1][c-1][0]=='w'): #right black capture
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append(Move((r,c),(r+1,c-1),self.board))
                
            if c+1<=7:
                if(self.board[r+1][c+1][0]=='w'): #left black capture
                    if not piecePinned or pinDirection == (1,1):
                        moves.append(Move((r,c),(r+1,c+1),self.board))

        #Add pawn promotions and en-passant
            
    #get all rook moves
    def getRookMoves(self,r,c,moves):

        piecePinned = False

        pinDirection = ()

        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1]!='Q': #can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break


        directions = [(-1,0),(1,0),(0,1),(0,-1)]
        enemycolor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i

                if 0<=endRow<8 and 0<=endCol<8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
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

        piecePinned = False

        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        
        directions = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        allycolor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r+d[0]
            endCol = c+d[1]
            if 0<=endRow<8 and 0<=endCol<8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allycolor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))

    #get all Bishop moves
    def getBishopMoves(self,r,c,moves):

        piecePinned = False

        pinDirection = ()

        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        

        directions = [(-1,-1),(-1,1),(1,-1),(1,1)] # Exactly same with rook moves, with different directions.
        enemycolor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i

                if 0<=endRow<8 and 0<=endCol<8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
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
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allycolor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]

            if 0<=endRow<8 and 0<=endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0]!=allycolor:
                    if allycolor=="w":
                        self.whiteKingLocation = (endRow,endCol)
                    else:
                        self.blackKingLocation = (endRow,endCol)
                inCheck,pins,checks = self.checkForPinsAndChecks()
                if not inCheck:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
                if allycolor=="w":
                    self.whiteKingLocation = (r,c)
                else:
                    self.blackKingLocation = (r,c)
    
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
    
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    
    #generate all castle moves
    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return #cant castle white we are in check.
        if(self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r,c,moves)
        if(self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r,c,moves)
        
    
    def getKingSideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))

    def getQueenSideCastleMoves(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))


class CastlingRights():
    def __init__(self,bks,bqs,wqs,wks):
        self.bks = bks
        self.bqs = bqs
        self.wqs = wqs
        self.wks = wks

class Move():

    ranksToRows = {"1":7, "2":6 , "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}

    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}

    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self,startSq,endSq,board,isCastleMove = False):

        self.startRow = startSq[0]
        self.startCol = startSq[1]

        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.moveId = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

        self.isCastleMove = isCastleMove

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

