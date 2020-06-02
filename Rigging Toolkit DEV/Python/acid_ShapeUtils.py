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