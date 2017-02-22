import os


def getCommType():
    #    print("getcommtype")
    return {"file": ("CommFile", checkFiles, __name__)}


def checkFiles(files):

    good = []
    conflict = []
    wrong = []

    for file in files:

        # check if path is path to file,
        if os.path.isfile(file) is False:
            pass
            #raise AttributeError("Attribute " + file + " is not file")

        writeable = os.access(file, os.W_OK)  # check if it is possible to write into file
        if writeable is False:
            pass
            #raise AttributeError("It is not possible to write into file '" + file + "'")

    return (good, conflict, wrong)
