import os
import sys

def checkPath(path_to_check):
    if not os.path.isdir(path_to_check):
        print("Path %s does not exists ! Exiting" % path_to_check)
        sys.exit(0)

def checkFile(file_to_check):
    if not os.path.exists(file_to_check):
        print("File %s does not exists ! Exiting" % file_to_check)
        sys.exit(0)
