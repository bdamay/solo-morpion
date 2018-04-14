__author__ = 'benoit'
import os, sys, getopt
import datetime as dt
from morpion.game import *
from morpion.ui import *

def main(argv):

    usage = 'python main.py [-s] [-f filename]  \n -s: launch solver without ui \n -f: specify filename'
    print('main')
    debut = dt.datetime.now()
    print('Starting at: ' + str(debut))
    try:
        opts, args = getopt.getopt(argv,"sf:d")
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    mode = 'ui'
    maxMoves, depth = 1000, 2

    filename = None
    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-s", "--solve"):
            mode = 'solver'
            maxMoves = int(arg) if args else 1000000000
        elif opt in ("-f", "--file"):
            filename = arg
        elif opt in ("-d", "--depth"):
            mode = "depth"
            depth = int(arg)


    sol = Solitaire()
    if filename:
        file = open(filename,'rb')
        sol = Solitaire.loadFromFile(filename)
        file.close()
    else:
        sol = Solitaire()


    if mode == 'solver':
        solver = Solver(sol)
        solver.solve()
        sol.saveToFile()

    else:
        ui = SolitaireUI(sol)
        ui.show()

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
