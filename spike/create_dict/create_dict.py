def create1():
	d1 = {"aa": "a", "bb":"b"}
	return d1

def create2():
	d2 = dict(aa="a", bb="b")
	return d2

d11 = create1()
d12 = create1()
print id(d11), id(d12)
d11["cc"] = "c"
print d12

d21 = create2()
d22 = create2()
print id(d21), id(d22)
d21["cc"] = "c"
print d22
