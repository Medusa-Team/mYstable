import os

def getCommType():
#    print("getcommtype")
    return {"file": ("CommFile", checkFile, __name__)}

def checkFile(files):

    for file in files:
        writeable = os.access(file, os.W_OK)  # check if it is possible to write into file
        if writeable is False:
            raise AttributeError("It is not possible to write into file '" + file + "'")