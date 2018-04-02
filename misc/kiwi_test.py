import kiwisolver as kiwi

# 0|-------------| x1 ----- xm ----- x2 |-----------------------|100
x1 = kiwi.Variable('x1')
x2 = kiwi.Variable('x2')
xm = kiwi.Variable('xm')
sm = kiwi.Variable('xm')

constraints = [
    x1 >= 0,
    x2 <= 100,
    x2 >= x1 + 10,
    sm == (x1 + x2),
    xm == (x1 + x2) / 2,
]  # these all have strength 'required'

solver = kiwi.Solver()
for cn in constraints:
    solver.addConstraint(cn)

solver.addEditVariable(xm, 'weak')
solver.min(sm, 50)

for val in (-20, 0, 20, 50, 80, 100, 140):
    solver.suggestValue(xm, val)
    solver.updateVariables()
    print('x1:', x1.value())
    print( 'x2:', x2.value())
    print('xm:', xm.value())
    print('sm:', sm.value())
    print( 'suggested xm:', val)
