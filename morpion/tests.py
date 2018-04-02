__author__ = 'benoit'

from morpion.game import *
import unittest

class MorpionsTest(unittest.TestCase):

    def test_line_gap(self):
        """Test le fonctionnement de la fonction gap"""
        l1 = Line((6,6), (6,10))
        l2 = Line((6,14),(6,18))
        # these ar 2 valid lines with no gap => gap should be -1
        gap = l1.getGapWith(l2)
        self.assertEquals(gap,4)


        l1 = Line((6,7), (6,11))
        l2 = Line((6,14),(6,18))
        # these ar 2 valid lines with no gap => gap should be -1
        gap = l1.getGapWith(l2)
        self.assertEquals(gap,3 )


        l1 = Line((12,14),(16,10))
        l2 = Line((7,19),(11,15))
        gap = l1.getGapWith(l2)
        self.assertEquals(gap,1)



if __name__ == '__main__':
    unittest.main()