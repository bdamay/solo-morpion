__author__ = 'benoit'

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import multiprocessing, time, threading
from .game import *
from .solver import *


class SolitaireUI:
    def __init__(self, solitaire):
        self.solitaire = solitaire
        self.board = self.solitaire.board
        self.fig, self.ax = plt.subplots()

        #Positionnement des boutons et du texte (système d'axes)
        self.btnUndo =plt.axes([0.7, 0.91, 0.1, 0.05])
        self.btnGoToStart =plt.axes([0.80, 0.91, 0.05, 0.05])
        self.btnBack =plt.axes([0.85, 0.91, 0.05, 0.05])
        self.btnNext =plt.axes([0.90, 0.91, 0.05, 0.05])
        self.btnGotoEnd =plt.axes([0.95, 0.91, 0.05, 0.05])
        self.btnSearch = plt.axes([0, 0.91, 0.1, 0.05])
        self.btnStopsearching = plt.axes([0.2, 0.91, 0.2, 0.05])


        self.btnSave = plt.axes([0, 0, 0.1, 0.05])
        self.btnLoad = plt.axes([0.2, 0, 0.1, 0.05])

        self.solver = None
        self.possibleMoves = []  #list of possible Moves that are drawn
        self.possibleMovesPoints = []  #reference to the possible moves points on the canvas
        self.movePoints =[]

        self.plotIndex = 0
        self.startPoint = 0

    def show(self):
        self.ax.clear()
        self.plotIndex = 0

        self.title = self.ax.text(1,1, 'Solitaire ')
        self.title.set_backgroundcolor('w')
        # set axes
        self.ax.set_xlim(0,len(self.board[:,0]))
        self.ax.set_ylim(0,len(self.board[0]))
        self.ax.set_xticks(range(0,len(self.board[:,0])))
        self.ax.set_yticks(range(0,len(self.board[0])))

        #grid
        pts = self.solitaire.getGrid()
        x = list([p[0] for p in pts])
        y = list([p[1] for p in pts])
        self.ax.scatter(x,y,s=1, color='g', linestyle='-')

        # points
        pts  = self.solitaire.getStartingPawns()
        x = list([p[0] for p in pts])
        y = list([p[1] for p in pts])

        self.ax.scatter(x,y, s=50, color='b', linestyle='-')


        self.plotPossibleMoves()

        # draw all lines
        if len(self.solitaire.moves) > 0 :
            for m in self.solitaire.moves:
                self.plotMove(m)

        self.fig.canvas.mpl_connect('button_press_event', self.onButtonPressed)

        self.fig.canvas.mpl_connect('button_release_event', self.onButtonReleased)


        bundo = Button(self.btnUndo, 'Undo')
        bundo.on_clicked(self.undo)


        btgotoend = Button(self.btnGotoEnd, '>>')
        btgotoend.on_clicked(self.navigateEnd)
        bnext = Button(self.btnNext, '>')
        bnext.on_clicked(self.navigateNext)
        bback = Button(self.btnBack, '<')
        bback.on_clicked(self.navigateBack)
        btgotostart = Button(self.btnGoToStart, '<<')
        btgotostart.on_clicked(self.navigateStart)

        bsearch = Button(self.btnSearch, 'Search')
        bsearch.on_clicked(self.getBestGame)
        bstop = Button(self.btnStopsearching, 'Stop Searching')
        bstop.on_clicked(self.stopSolver)


        bsave = Button(self.btnSave, 'Save')
        bsave.on_clicked(self.saveGame)

        bload = Button(self.btnLoad, 'Load')
        bload.on_clicked(self.loadGame)


        plt.show()



    def getBestGame(self, event):

        self.solitaire.starttime = dt.datetime.now()
        self.startPoint = len(self.solitaire.moves)
        if self.solver == None:
            self.solver = Solver(self.solitaire)
        else:
            self.solver.hasBeenSearched.remove(self.solitaire.getHash())
            self.solver = Solver(self.solitaire, self.solver.hasBeenSearched)

        thread = threading.Thread(target=self.solver.solve)
        thread.start()
        print('check thread')


    def stopSolver(self, event):
        if self.solver:
            self.solver.stopSolver()
            print('stopping the solver')
        self.solitaire = self.solver.bestGame
        self.ax.clear()
        self.show()

    def onButtonPressed(self, event):
        """
        ‘key_press_event’	KeyEvent - key is pressed
        Retrieve the actual coordinate of point starting a line
        Solitaire UI is in state moveStarted true
        :return:
        """
        if event.xdata and event.ydata:
            self.currentStartPoint =(int(round(event.xdata)),int(round(event.ydata)))

    def onButtonReleased(self, event):
        """
        Retrieve x,y coordinates of the second point and try to play a move.
        If move not valid - moveStarted gets to be false
        :return:
        """
        if self.plotIndex != len(self.solitaire.moves):
            print('cannot play while navigating the game')
            return
        if event.xdata and event.ydata:
            currentEndPoint = (int(round(event.xdata)),int(round(event.ydata)))
            print(currentEndPoint)
            newline = self.solitaire.addMove(self.currentStartPoint, currentEndPoint)
            if newline:
                self.plotMove(self.solitaire.moves[-1]) #last line

    def plotMove(self, move):
        """
        plot a line with missing point in red and line
        @:param: Move
        """
        if self.possibleMovesPoints:
            self.cleanPossibleMoves()

        #plot point + line
        scat = self.ax.scatter(move.point[0], move.point[1], color='r')
        self.movePoints.append(scat)
        self.plotIndex += 1
        self.ax.plot((move.line.p1[0], move.line.p2[0]), (move.line.p1[1], move.line.p2[1]), color='r', linestyle='-')
        s = 'Moves: ' +str(self.plotIndex)+'/'+ str(len(self.solitaire.moves))
        self.title.set_text(s)
        if self.plotIndex == len(self.solitaire.moves):
            self.plotPossibleMoves()
        plt.draw()

    def undo(self,event):
        if self.plotIndex != len(self.solitaire.moves):
            print('cannot undo if navigating the game')
            return
        self.cleanPossibleMoves()
        m = self.solitaire.undoLastMove()
        self.plotIndex -= 1

        #remove line
        self.ax.get_lines().pop().remove()
        self.movePoints.pop().remove()

        for pt in m.line.points:
            if self.solitaire.board[pt[0],pt[1]] == 0:
                self.ax.scatter(pt[0], pt[1], s=1, color='g')

        s = 'Moves: ' +str(self.plotIndex)+'/'+ str(len(self.solitaire.moves))
        self.title.set_text(s)
        self.plotPossibleMoves()
        plt.draw()

    def unplotMove(self,m):
        """

        :param Move m:
        :return:
        """
        self.cleanPossibleMoves()
        #remove line
        self.ax.get_lines().pop().remove()
        self.movePoints.pop().remove()
        for pt in m.line.points:
            if self.solitaire.board[pt[0],pt[1]] == 0:
                self.ax.scatter(pt[0], pt[1], s=1, color='g')
        self.plotIndex -= 1
        s = 'Moves: ' +str(self.plotIndex)+'/'+ str(len(self.solitaire.moves))
        self.title.set_text(s)

        plt.draw()

    def cleanPossibleMoves(self):
        #erase previous possible moves
        for m in self.possibleMovesPoints:
            try:
                m.remove()
            except:
                pass


        self.possibleMovesPoints = []

    def plotPossibleMoves(self):
        #plot possible moves
        self.possibleMoves = self.solitaire.getPossibleMoves()
        for move in self.possibleMoves:
            pt = self.ax.scatter(move.point[0], move.point[1], color='tomato', s=8)
            self.possibleMovesPoints.append(pt)
        plt.draw()

    def saveGame(self, event):
        self.solitaire.saveToFile()

    def loadGame(self, event):
        new_solitaire = self.solitaire.loadFromFile('data/game.dmp')
        self.solitaire = new_solitaire
        self.show()

    def navigateNext(self, event):
        if self.plotIndex < len(self.solitaire.moves):
            self.plotMove(self.solitaire.moves[self.plotIndex])

    def navigateBack(self, event):
        if self.plotIndex >0:
            self.unplotMove(self.solitaire.moves[self.plotIndex-1])

    def navigateEnd(self, event):
        while self.plotIndex < len(self.solitaire.moves):
            self.plotMove(self.solitaire.moves[self.plotIndex])

    def navigateStart(self, event):
        while self.plotIndex > self.startPoint:
            self.unplotMove(self.solitaire.moves[self.plotIndex-1])
        self.startPoint = 0
