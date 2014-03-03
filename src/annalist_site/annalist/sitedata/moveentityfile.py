import os, os.path
import shutil

for f in os.listdir("."):
	if os.path.isfile(f) and f.endswith(".jsonld"):
		fstem = f[:-7]
		print "os.mkdir %s"%fstem
		os.mkdir(fstem)
		print "shutil.copyfile %s %s"%(f, fstem+"/enum_meta.jsonld")
		shutil.copyfile(f, fstem+"/enum_meta.jsonld")
