
def AverageVector3(VectorList):
    # get the position average (center)
    # very slow on big old selections
    sumX, sumY, sumZ = 0.0, 0.0, 0.0
    length = len(VectorList)

    for vector in VectorList:
        sumX += vector[0]
        sumY += vector[1]
        sumZ += vector[2]
    
    if(length == 0):
        return [0,0,0]
        
    return [sumX / length, sumY / length, sumZ / length]