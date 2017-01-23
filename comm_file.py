import os

def getCommType():
#    print("getcommtype")
    return {"file": ("CommFile", checkFile, __name__)}

def checkFile(files):

    for file in files:

        #check if path is path to file,
        if os.path.isfile(file) is False:
            raise AttributeError("Attribute " + file + " is not file")

        writeable = os.access(file, os.W_OK)  # check if it is possible to write into file
        if writeable is False:
            raise AttributeError("It is not possible to write into file '" + file + "'")