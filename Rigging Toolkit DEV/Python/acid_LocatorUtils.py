from maya import cmds


def AveragePosFromVerts(vertList):
    # get the position average (center)
    # very slow on big old selections
    sumX, sumY, sumZ = 0.0, 0.0, 0.0
    length = len(vertList)

    for vert in vertList:
        pos = cmds.pointPosition(vert, world=True)
        sumX += pos[0]
        sumY += pos[1]
        sumZ += pos[2]
    
    if(length == 0):
        return [0,0,0]
        
    return [sumX / length, sumY / length, sumZ / length]


def LocatorAtPos(pos):from maya import cmds


def AveragePosFromVerts(vertList):
    # get the position average (center)
    # very slow on big old selections
    sumX, sumY, sumZ = 0.0, 0.0, 0.0
    length = len(vertList)

    for vert in vertList:
        pos = cmds.pointPosition(vert, world=True)
        sumX += pos[0]
        sumY += pos[1]
        sumZ += pos[2]
    
    if(length == 0):
        return [0,0,0]
        
    return [sumX / length, sumY / length, sumZ / length]


def LocatorAtPos(pos, name):
    # create a locator moved to the desired worldspace location
    locName = name + "_LOC"
    sel = cmds.spaceLocator()
    cmds.setAttr(sel[0] + ".translateX", pos[0])
    cmds.setAttr(sel[0] + ".translateY", pos[1])
    cmds.setAttr(sel[0] + ".translateZ", pos[2])
    renamedLoc = cmds.rename(sel, locName)
    return renamedLoc


def LocatorAtSelectionCenter():
    # turn selection into a vert selection
    lsCon = cmds.polyListComponentConversion(toVertex=True)
    cmds.select(lsCon)
    # turn into nice list
    lsVerts = cmds.ls(sl=True, flatten=True)
    center = AveragePosFromVerts(lsVerts)
    # create the locator
    return LocatorAtPos(center)


    # create a locator moved to the desired worldspace location
    sel = cmds.spaceLocator()
    cmds.setAttr(sel[0] + ".translateX", pos[0])
    cmds.setAttr(sel[0] + ".translateY", pos[1])
    cmds.setAttr(sel[0] + ".translateZ", pos[2])
    return sel[0]


def LocatorAtSelectionAverage(name):
    # turn selection into a vert selection
    lsCon = cmds.polyListComponentConversion(toVertex=True)
    cmds.select(lsCon)
    # turn into nice list
    lsVerts = cmds.ls(sl=True, flatten=True)
    center = AveragePosFromVerts(lsVerts)
    # create the locator
    return LocatorAtPos(center, name)

