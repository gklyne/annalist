class A(object):
     def __init__(self, baseval):
         self._baseval = baseval;
         return
     def objval(self, val):
         return self._baseval+val

a = A("a")
a.objval("b")
