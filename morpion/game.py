__author__ = 'benoit'

import datetime as dt
import os, sys, getopt
import hashlib
import pickle
import numpy as np
from collections import Counter

from .ui import *
from .solver import *



class Move:
    def __init__(self, point, line):
        self.point = point
        self.line = line

    def __str__(self):
        return str(self.point)

class Line:
    """
    Line length is always 4 (ie 4 intervals between 5 points)
    Line instance is carrying a list of lines that it overlaps that is initialized with solitaire game
     """
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        if self.p1 > self.p2: #switching points if p1 > p2 (for sorting reasons)
            p2 = self.p1
            self.p1 = self.p2
            self.p2 = p2
        self.dir= self.getDirection() # getting the direction of the line (frome beginning to the end)
        self.origin = self.getOrigin()
        self.points = [(self.p1[0] + x*self.dir[0],self.p1[1] +x*self.dir[1]) for x in range(5)] # list of coords of points for the line
        self.overlaps = []

    def isValid(self):
        """
        A valid line is a line that is len 4 and whiwh the direction is valid
        :return: boolean
        """
        #Check length at least x2-x1= 4 or y2-y1=4
        xgap = abs(self.p1[0]-self.p2[0])
        ygap = abs(self.p1[1]-self.p2[1])
        tot= xgap+ygap
        return (xgap == 4 or ygap == 4) and (tot == 4 or tot == 8)

    def getDirection(self):
        """
        Return the couple of integer that represents a direction from startpoint to endpoint of line
        :return: (1,0) or (0,1) etc.. or None
        """
        return (int((self.p2[0]-self.p1[0])/4), int((self.p2[1]-self.p1[1])/4))

    def getOrigin(self):
        """
        :return: tuple (0,N) or (1,N) where 0 is x axe and 1 is y axe and N the origin on the axe
        """
        if self.dir==(0,1):
            return (0,self.p1[0])
        if self.dir == (1,0):
            return (1,self.p1[1])
        if self.dir == (1,1):
            dif = self.p1[0]-self.p1[1]
            return (0 if dif >= 0 else 1, abs(dif))
        if self.dir == (1,-1):
            return (1, self.p1[0]+self.p1[1]) #only on y axe

    def isOverlapping(self, otherline):
        """
        Checks whether 2 lines ovelaps
        :param Line otherline:
        :return:boolean
        """
        if self.dir != otherline.dir:
            return False
        if otherline in self.overlaps or self in otherline.overlaps:
            return True
        intersect = set(self.points).intersection(set(otherline.points))
        if len(intersect) > 1:
            return True
        return False


    def __str__(self):
        return str(sorted([self.p1,self.p2])).replace(' ','')

    def equals(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def isAdjacentTo(self,otherline):
        if self.dir != otherline.dir:
            return False
        return self.p1 == otherline.p2 or self.p2 == otherline.p1

    def getGapWith(self, otherline):
        """
        :param Line otherline:
        :return: int
        """
        if self.dir != otherline.dir or self.origin != otherline.origin:
            return -1
        else:
            divisor = sum(self.dir)
            if divisor == 0: divisor = 2 #(1,-1 direction)
            return abs((sum(self.p1) - sum(otherline.p1))//divisor)-4

class Solitaire:

    global bestline, bestscore, hasBeenSearched, totalMovesPlayed
    def __init__(self):
        self.moves = []
        self.board = np.array([
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,2,2,2,2,0,0,2,2,2,2,0,0,0],
            [0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,2,0,0,0],
            [0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,2,0,0,0],
            [0,0,0,0,0,0,0,0,0,2,2,2,2,0,0,2,2,2,2,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,2,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])

        self.hash = self.getHash()
        self.possiblemoves = {} # hash of game with possible moves association
        self.width = len(self.board)
        self.height = len(self.board[0])

        #trying to represent game with a space of 4 dimensions N, NE, E, SE
        #giving better aprehension of the 4 dirs of the game

        self.starttime = (dt.datetime.now())
        self.allLines = self.getAllPossibleLines() #stocke toutes les définitiones de lignes possibles
        self.getPossibleMoves()

    def saveToFile(self, filename=None):
        if filename is None:
            filename = 'data/game.dmp'
        file = open(filename,'wb')
        #provisoire clean le tableau de hash
        self.possiblemoves.clear()
        dump = pickle.dump(self, file)
        file.close()

    def loadFromFile(self, filename):
        file = open(filename,'rb')
        game = pickle.load(file)
        file.close()
        return game



    def getGrid(self):
        """
        Returns grid with 1 point on each 0 value of the grid
        :return: list
        """
        ii = np.where(self.board == 0)
        l = list(zip(*ii))
        return l

    def getStartingPawns(self):
        """
        Returns points of the board with 1 point with value of it in the grid
        :return: list
        """
        ii = np.where(self.board == 2)
        l = list(zip(*ii))
        return l

    def addMove(self, p1, p2):
        """
        add Move from boundaries (called from UI)
        :param p1:
        :param p2:
        :return: None
        """
        newLine = Line(p1,p2) #self.allLines.get(str(sorted([p1,p2])).replace(' ','')) ## alllines should be a dictionnary ?
        for l in self.allLines: # getting the reference of the line in allLines
            if newLine.equals(l):
                newLine = l
        return self.addMoveFromLine(newLine)

    def addMoveFromLine(self, newLine):
        if newLine and newLine.isValid():
            newmove = self.getValidMoveFromLine(newLine)
            if newmove:
                self.playMove(newmove)
                return newmove

        print('move is not valid')
        return None

    def playMove(self, move):
        """
        Play a move without verifying
        :param move:
        :return: move
        """
        self.moves.append(move)
        self.board[move.point[0],move.point[1]] = 1
        self.hash = self.getHash()


    def checkMoveFromLine(self, line):
        if line.isValid():
            return self.getValidMoveFromLine(line)
        return None

    def undoLastMove(self):
        if len(self.moves) > 0:
            m = self.moves.pop()
            self.board[m.point[0],m.point[1]] = 0
            self.hash = self.getHash()
            return m
        return None

    def getValidMoveFromLine(self, line):
        """
        check if move (line instance) is valid in the board.
        Valid means: the line is 4 length crossed 4 points and one free space on the board
        the move will be one point and a line
        :param line: line (2 points) tuple
        :return: move (valid one) or None
        """
        if not line.isValid(): #line must be OK at first
            return None
        linePattern = [self.board[p[0],p[1]] for p in line.points]

        #one and only one coord must be empty DONE optimising with Counter
        if Counter(linePattern)[0] != 1:
            return None
        for l in [m.line for m in self.moves]:
            if l in line.overlaps:
                return None
        return Move(line.points[linePattern.index(0)],line)
        #First we retrieve all coords on line

    def getAllPossibleLines(self):
        """
        :return: list of all lines - initialisation of overlapping lines
        That done we don't have to instanciate new lines -
        """
        lines = []
        lenX = len(self.board)
        lenY = len(self.board[0])
        for j in range(lenY):
            for i in range(lenX):
                if j+4 < lenY:
                    lines.append(Line((i,j),(i,j+4)))
                if j+4 < lenY and i+4 < lenX:
                    lines.append(Line((i,j),(i+4,j+4)))
                if i+4 < lenX:
                    lines.append(Line((i,j),(i+4,j)))
                if j >4 and i+4 < lenX:
                    lines.append(Line((i,j),(i+4,j-4)))
        for line in lines:
            for l2 in lines: #cross join check
                if line.isOverlapping(l2):
                    line.overlaps.append(l2) #add this element to the line

        print('end of init lines: '+ str(dt.datetime.now()))
        return lines # make dictionary


    def getPossibleMoves(self):

        return self.__calculatePossibleMoves()

    def __calculatePossibleMoves(self):
        moves = []
        # for each line possible of the board, check if it is a possible move.
        # TODO optimize without allline stuff ??
        # allLines should be allPlayableLines for the current instance of the game
        for l in self.allLines:
            m = self.getValidMoveFromLine(l)
            if m:
                moves.append(m)
        return moves

    def getHash(self):
        s = ''.join([str(item) for sublist in self.board for item in sublist]) #the board
        s += ':'+str(sorted( [str(m.line) for m in self.moves])) #sorted lines
        hash_object = hashlib.md5(s.encode())
        return hash_object.hexdigest()

