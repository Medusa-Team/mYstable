import os
import subprocess


def getCommType():
    #    print("getcommtype")
    return {"file": ("CommFile", checkFiles, __name__)}


def checkFiles(hosts, good, conflict, wrong):

    # good - no conflicts, file reachabe
    # conflict - files reachable, but files points to equal inode eg. hard links / sym links
    # wrong - not reachable files at all

    inodes = dict() #mapping inode -> host(s)


    for host in hosts:
        # check if path is path to file,
        file = host['host_commdev']

        if os.path.isfile(file) is False:
            wrong.append(host)
            continue

        writeable = os.access(file, os.W_OK)  # check if it is possible to write into file
        if writeable is False:
            wrong.append(host)
            continue

        # result of command is '<device_number_decimal>:<inode_number>'
        stat_cmd = 'stat -Lc "%d:%i" ' + file
        stat_info = subprocess.check_output(stat_cmd, shell=True)
        stat_info = stat_info.decode()

        inodes.setdefault(stat_info, []).append(host)

    for value in inodes.values():
        # couple hosts are sharing one inode - conflict
        if len(value) > 1:
            conflict.extend(value)
        else:
            # inode is owned by unique file
            good.append(value)
