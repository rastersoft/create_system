#!/usr/bin/env python3

import shutil
import os
import sys
import subprocess
import errno
from os import makedirs

def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


if len(sys.argv) > 1:
    config_path = sys.argv[1]
else:
    config_path = "/etc/webtv.system" 

config = open(config_path,"r")

system_path = "/final_system/bg_apps"
binaries = []
folders = []
files = []
links = []
touch = []

for l in config:
    l = l.strip()
    if l == "":
        continue
    if l[0] == '#':
        continue
    pos1 = l.find(":")
    pos2 = l.find("=")
    if (pos1 == -1) and (pos2 == -1):
        continue
    if (pos1 == -1) or ((pos2 != -1) and (pos2 < pos1)):
        pos1 = pos2
    etype = l[0:pos1].strip()
    edata = l[pos1+1:].strip()

    if etype == "system_path":
        system_path = edata
        continue
    if etype == "binary":
        if binaries.count(edata) == 0:
            binaries.append(edata)
        continue
    if etype == "copy":
        if os.path.isdir(edata):
            if edata[-1] == '/':
                edata = edata[1:]
            if folders.count(edata) == 0:
                folders.append(edata)
        else:
            if files.count(edata) == 0:
                files.append(edata)
        continue
    if etype == "link":
        links.append(edata)
        continue
    if etype == "touch":
        touch.append(edata)
        continue


found_error = False

for element in binaries:
    if element[0] == '/':
        binary = element[:]
        if not os.path.exists(binary):
            found_error = True
            print("Can't find binary {:s}\n".format(str(element)))
            continue
    else:
        binary = None
        for p in ["/sbin","/usr/sbin","/usr/local/sbin","/bin","/usr/bin","/usr/local/bin"]:
            fpath = os.path.join(p,element)
            if os.path.exists(fpath):
                binary = fpath[:]
                break
        if binary == None:
            print("Can't find binary {:s}\n".format(str(element)))
            found_error = True
            continue

    files.append(binary)
    retproc = subprocess.Popen(["/usr/bin/ldd",binary],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = retproc.communicate()
    if 0 != retproc.wait():
        print("Can't get dependencies for static program {:s}".format(binary))
        continue
    for dline in stdoutdata.decode("utf8").split("\n"):
        pos = dline.find("=>")
        if pos == -1:
            library = dline.strip().split(" ")[0]
        else:
            library = dline[pos+2:].strip().split(" ")[0]
        if library == "":
            continue
        if (0 == files.count(library)) and (library[0] == '/'):
            files.append(library)

if found_error:
    sys.exit(1)

shutil.rmtree(system_path, ignore_errors = True)
os.makedirs(system_path)

for f in files:
    while f != None:
        folder,filename = os.path.split(f)
        final_path = os.path.join(system_path,folder[1:])
        makedirs(final_path,exist_ok = True)
        shutil.copy2(f,final_path,follow_symlinks=False)
        if os.path.islink(f):
            f = os.path.realpath(f)
        else:
            f= None

for f in folders:
    folder,filename = os.path.split(f)
    final_path = os.path.join(system_path,folder[1:])
    final_path2 = os.path.join(system_path,f[1:])
    makedirs(final_path,exist_ok = True)
    shutil.copytree(f,final_path2)

for f in links:
    l1 = f.split(" ")[0]
    l2 = f.split(" ")[1]
    if (l1[0] == '/'):
        l1 = l1[1:]
    l1 = os.path.join(system_path,l1)
    if not os.path.exists(l1):
        os.symlink(l2,l1)

for f in touch:
    if f[0] == '/':
        f = f[1:]
    os.system("touch {:s}".format(os.path.join(system_path,f)))
