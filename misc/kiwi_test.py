import kiwisolver as kiwi

# 0|-------------| x1 ----- xm ----- x2 |-----------------------|100
x1 = kiwi.Variable('x1')
x2 = kiwi.Variable('x2')
xm = kiwi.Variable('xm')
sm = kiwi.Variable('sm')
sm2 = kiwi.Variable('sm')



constraints = [
    x1 >= 0,
    x2 <= 100,
    x2 >= x1 + 10,
    xm == (x1 + x2) / 2,
    sm == x1 + x2 ,
]  # these all have strength 'required'

solver = kiwi.Solver()
for cn in constraints:
    solver.addConstraint(cn)




solver.addEditVariable(xm, 'strong')
solver.addEditVariable(sm, 'weak')

solver.addConstraint(sm >= 100)
solver.suggestValue(xm, 40)
solver.updateVariables()
print('x1:', x1.value())
print( 'x2:', x2.value())
print('xm:', xm.value())
print('sm:', sm.value())
