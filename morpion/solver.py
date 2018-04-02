__author__ = 'benoit'
import datetime as dt
import random, copy

class Solver:
    def __init__(self, solitaire, maxMoves, depth):
        self.sol = solitaire
        self.bestGame = []
        self.bestscore = 0
        self.hasBeenSearched = []
        self.totalMovesPlayed = 0
        self.totalBoardEvaluation = 0
        self.totalMoveEvaluation = 0
        self.min = 0
        self.top = 0
        self.skipped = 0
        self.starttime = (dt.datetime.now())
        self.maxMoves = maxMoves
        self.stop = False
        self.depth = depth


    def solve(self):
        self.searchBestMove()
        print('Finished with best = '+str(self.bestscore))


    def searchDepth(self):
        self.searchInDepth(self.depth)

    def searchInDepth(self, depth):
        if depth == 0:
            linescore = self.evaluateBoard()
            if linescore > self.bestscore:
                self.bestGame = copy.deepcopy(self.sol)
                self.bestscore = linescore
                print('durée: ' +str(dt.datetime.now() - self.starttime) + ' bestscore ' + str(self.bestscore)  + ' totalMoves '+str(self.totalMovesPlayed) + ' totalEvaluations '+str(self.totalBoardEvaluation))
            self.sol.undoLastMove()
            return self.bestGame
        if self.sol.hash not in self.hasBeenSearched:
            self.hasBeenSearched.append(self.sol.hash)
            moves = self.sol.getPossibleMoves()
            # sort move with scores evaluation
            scores = self.getScores(moves)
            moves = [s[1] for s in sorted(zip(scores, moves), key=lambda pair: -pair[0])] #sort descending
            for m in moves:
                self.sol.playMove(m)
                self.totalMovesPlayed +=1
                self.bestGame = self.searchInDepth(depth-1)
        else:
            self.skipped += 1
        if self.depth <= depth+1:
            print('end depth'+str(depth)+' -- bestgame ' +str(self.bestscore) +' totalMoves '+str(self.totalMovesPlayed) + ' totalEvaluations '+str(self.totalBoardEvaluation)+ ' skipped '+str(self.skipped))
        self.sol.undoLastMove()
        return self.bestGame


    def searchBestMove(self):
        """
        Examine all branches and stores the best in bestGame
        :return: Move
        """
        if self.totalMovesPlayed > self.maxMoves or self.stop:
            self.sol.undoLastMove()
            return
        if self.totalMovesPlayed > 0 and self.totalMovesPlayed % 1000 == 0:
            print('durée: ' +str(dt.datetime.now() - self.starttime) + ' bestscore ' + str(self.bestscore) +' min:' +str(self.min)+ ' top:' +str(self.top)+ ' skipped:'+str(self.skipped) + ' totalMoves '+str(self.totalMovesPlayed) + ' totalEvaluations '+str(self.totalMoveEvaluation))
            self.top, self.min, self.skipped = 0, self.bestscore, 0

        if self.sol.hash not in self.hasBeenSearched:
            self.hasBeenSearched.append(self.sol.hash)
            moves = self.sol.getPossibleMoves()
            # sort move with scores evaluation
            scores = self.getScores(moves)
            moves = [s[1] for s in sorted(zip(scores, moves), key=lambda pair: -pair[0])] #sort descending
            for m in moves:
                self.sol.playMove(m)
                self.totalMovesPlayed +=1
                self.searchBestMove()
            linescore = len(self.sol.moves)
            self.top = linescore if linescore > self.top else self.top
            if linescore > self.bestscore:
                self.bestGame = copy.deepcopy(self.sol)
                self.bestscore = linescore
                print('durée: ' +str(dt.datetime.now() - self.starttime) + ' bestscore ' + str(self.bestscore)  + ' totalMoves '+str(self.totalMovesPlayed) + ' totalEvaluations '+str(self.totalMoveEvaluation))
                if self.bestscore >= 150:   #max for me
                    self.sol.saveToFile('data/game'+str(self.bestscore)+'-'+dt.datetime.now().strftime('%Y-%m-%d-%Hh%M')+'.dmp')
        else:
            self.skipped += 1
        self.sol.undoLastMove()
        mvs = len(self.sol.moves)
        self.min = mvs if mvs < self.min else self.min
        return self.bestGame

    def stopSolver(self):
        self.stop = True

    def evaluateBoard(self):
        """
        Static evaluation  of the game
        :return: int score
        not used
        """
        self.totalBoardEvaluation += 1
        #score = len(self.sol.getPossibleMoves())
        score = random.randrange(10)
        return score

    def getScores(self, moves):
        """
        Returns a list of scores foreach move of the list
        :param moves:
        :return: list
        """
        scores = []
        for m in moves:
            scores.append(self.evaluateMove(m))
        return scores

    def evaluateMove(self, m):
        self.totalMoveEvaluation += 1
        score = 0
        linesPlayed = [m.line for m in self.sol.moves]
        for l in linesPlayed:
            #get gap
            gap = m.line.getGapWith(l)
            if gap == 0:
                score +=100
            elif gap > 0 and gap < 4:   # a gap of 4 may signify a full line is in between
                score-=10**gap

        #minimizing x and maximizing y - for moving upleft to down right ?
        #score += m.line.p1[1]-m.line.p1[0]

        return score
        """
        Evaluate move statically with basic concepts
        1. Compacity  ? (how many neighbours for the new pawn)
        :param m: Move
        :return: integer
        neighbours = 0
        neighbours += 1 if self.sol.board[m.point[0]+1][m.point[1]] > 0 else 0
        neighbours += 1 if self.sol.board[m.point[0]+1][m.point[1]+1] > 0 else 0
        neighbours += 1 if self.sol.board[m.point[0]+1][m.point[1]-1] > 0 else 0
        neighbours += 1 if self.sol.board[m.point[0]-1][m.point[1]] > 0 else 0
        neighbours += 1 if self.sol.board[m.point[0]-1][m.point[1]+1] > 0 else 0
        neighbours += 1 if self.sol.board[m.point[0]-1][m.point[1]-1] > 0 else 0
        neighbours += 1 if self.sol.board[m.point[0]][m.point[1]-1] > 0 else 0
        neighbours += 1 if self.sol.board[m.point[0]][m.point[1]+1] > 0 else 0
        score += neighbours*10
        """

        """ Dynamic evaluation

        actual = len(self.sol.getPossibleMoves()) # possible moves before moving
        self.sol.playMove(m)
        pm = len(self.sol.getPossibleMoves()) # possible moves after moving
        self.sol.undoLastMove()
        score += 10*pm + 100*(pm-actual)

        return score
        """