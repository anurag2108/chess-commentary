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
        