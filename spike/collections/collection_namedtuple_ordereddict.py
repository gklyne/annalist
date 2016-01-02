from collections    import OrderedDict, namedtuple

od = OrderedDict(a="aaa", b="bbb")

nt = namedtuple("nt", ["x", "y"])

nt1 = nt(x=1, y=od)

print nt1

nt2 = nt(x=od, y="yyy")

print nt2

