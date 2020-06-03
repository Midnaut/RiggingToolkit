from maya import cmds

def makeControlPointsArray(points, path):
    ctlPoints = []
    for point in path:
        ctlPoints.append(points[point])
    return ctlPoints


def diamondControlPath():
    corners = [(0,0,-1),(1,0,0),(0,0,1),(-1,0,0),(0,1,0),(0,-1,0)]
    path = [0,1,2,3,0,4,2,5,0,1,4,3,5,1]  
    pathPoints = makeControlPointsArray(corners, path)    
    return pathPoints

def cubeControlPath():
    corners = [ (-1,1,-1), (1,1,-1), (1,-1,-1), (-1,-1,-1),(-1,1,1), (1,1,1), (1,-1,1), (-1,-1,1)]
    path = [0,1,2,3,0,4,5,6,7,4,5,1,0,4,7,3,0,1,2,6]
    pathPoints = makeControlPointsArray(corners, path)    
    return pathPoints

def sphereControl():
    shapeGrp = cmds.group(em=True, name="newSphere")
    circleA = cmds.circle(nr = [1,0,0])
    circleB = cmds.circle(nr = [0,1,0])
    circleC = cmds.circle(nr = [0,0,1])
    sphereControl = cmds.parent (cmds.listRelatives(circleA, s=1),cmds.listRelatives(circleB, s=1),cmds.listRelatives(circleC, s=1),shapeGrp, s=1, r=1)
    cmds.delete(circleA,circleB,circleC)
    return shapeGrp