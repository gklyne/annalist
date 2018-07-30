from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Definitions to support porting to Python 3

The intent is to abstract here those API calls used by Annalist that are 
sensitive to string vs unicode parameters.
"""

def encode_str(ustr):
	"""
	Return string value for supplied Unicode
	"""
	return ustr.encode('ascii', 'ignore')

str_space = encode_str(' ')

def isoformat_space(datetime):
	"""
	Return ISO-formatted date with space to separate date and time.
	"""
	return datetime.isoformat(str_space)
