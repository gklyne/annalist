class my_number(object):

    def __init__(self, n):
        self._n = n
        return

    def is_odd(self):
        return self._n % 2 == 1

    def is_even(self):
        return self._n % 2 == 0

    def __repr__(self):
        return "my_number(%d)"%(self._n)

list_n = [my_number(i) for i in range(10)]

list_odd = filter(my_number.is_odd, list_n)

list_even = filter(my_number.is_even, list_n)

my_number.is_even(list_n[0])

my_number.is_odd(list_n[0])

# my_number.is_even(2)

# TypeError: unbound method is_enum_field() must be called with FieldDescription instance as first argument 
#                                                          (got FieldDescription instance instead)