from typing import List, Set
import subprocess
import pathlib, os
from subprocess import Popen, PIPE


def installPackageWindows(dependencyFolders:Set[str], timeout=120, updateRequirements=False):
    
    packageFolder = getPackageToInstallFolder()

    if updateRequirements:
        print(f"*******Updating requirements*********")
        cmds = ['cd ' + packageFolder, 'poetry update']

        err = runWindowsCommandsV2(cmds, timeout=timeout)
        if  err != "":
            raise Exception(f"Poetry update failed for {packageFolder}: Error = {err}")
    
    for dependencyFolder in dependencyFolders:
        print(f"*******Installing dependency '{dependencyFolder}'*********")
        cmds = getDependencyCommands(dependencyFolder)

        err = runWindowsCommandsV2(cmds, timeout=timeout)
        if  err != "":
            raise Exception(f"Poetry install failed for {dependencyFolder}: Error = {err}")


    print(f"*******Installing package*********")
    cmds = ['cd ' + getPackageToInstallFolder(), 'poetry install']

    err = runWindowsCommandsV2(cmds, timeout=timeout)
    if  err != "":
        raise Exception(f"Poetry install failed for {packageFolder}: Error = {err}")



def runWindowsCommands(cmds:List[str]):
    
    with Popen( "cmd.exe", shell=False, universal_newlines=True,
                    stdin=PIPE, stdout=PIPE, stderr=PIPE ) as process:  
        for cmd in cmds:
            process.stdin.write(cmd + "\n")
            # print(process.stderr.read())
        process.stdin.close()
        print(process.stdout.read())
        # print(process.stderr.read())

    return True

def runWindowsCommandsV2(cmds:List[str], timeout=120):
    
    with Popen( "cmd.exe", shell=False, universal_newlines=True,
                    stdin=PIPE, stdout=PIPE, stderr=PIPE ) as process:  
        cmdStr = "\n ".join(cmds) + "\n"
        
        
        outs, errs = process.communicate(cmdStr, timeout=timeout)
        # process.stdin.close()
        # print(process.stdout.read())
        print("Stdout:", outs)
        print("Stderr:", errs)
        return errs
        


def installPackagePosix(dependencyFolders:Set[str]):
    
    packageFolder = getPackageToInstallFolder()
    print(f"*******Updating requirements*********")
    cmds = ['cd ' + packageFolder, 'poetry update']
    runPosixCommands(cmds)
    if runPosixCommands(cmds) != "":
        raise Exception(f"Poetry update failed for {packageFolder}")
    
    for dependencyFolder in dependencyFolders:
        print(f"*******Installing dependency '{dependencyFolder}'*********")
        cmds = getDependencyCommands(dependencyFolder)
        if runPosixCommands(cmds) != "":
            raise Exception(f"Poetry install failed for {dependencyFolder}")
            

    print(f"*******Installing package*********")
    cmds = ['cd ' + getPackageToInstallFolder(), 'poetry install']
    runPosixCommands(cmds)
    if runPosixCommands(cmds) != "":
        raise Exception(f"Poetry install failed for {packageFolder}")

def runPosixCommands(cmds:List[str]):
    
    commandStr = "; ".join(cmds)
    process = subprocess.run(commandStr, 
                         shell=True,
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         universal_newlines=True
                         )

    print("Stdout:", process.stdout)
    print("Stderr:", process.stderr)
    
    return process.stderr


def getPackageToInstallFolder():
    packageFolder = pathlib.Path().resolve().as_posix()
    return packageFolder

def getPackageRootPath():
    cwd = pathlib.Path().resolve()
    parentPath = cwd.parent.as_posix()
    return parentPath


def getDependencyPath(dependencyName):
    parentPath = getPackageRootPath()
    dependencyPath = os.path.join(parentPath, dependencyName)
    return dependencyPath

def getDependencyCommands(dependencyName):
    dependencyPath = getDependencyPath(dependencyName=dependencyName)
    cmds = ['cd ' + dependencyPath, 'poetry install']
    return cmds


