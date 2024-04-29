import math

def rotatePolygon(polygon, theta, center):
    """Rotates the given polygon which consists of corners represented as (x,y),
    around the ORIGIN, clock-wise, theta degrees"""
    theta = math.radians(theta)
    rotatedPolygon = []
    for corner in polygon :
        rotatedPolygon.append(( (corner[0] - center[0])*math.cos(theta)-(corner[1] - center[1])*math.sin(theta) + center[0], (corner[0] - center[0])*math.sin(theta)+(corner[1] - center[1])*math.cos(theta) + center[1]) )
    return rotatedPolygon

def rotatePoint(centerPoint,point,angle):
    """Rotates a point around another centerPoint. Angle is in degrees.
    Rotation is counter-clockwise"""
    angle = math.radians(angle)
    temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
    temp_point = ( temp_point[0]*math.cos(angle)-temp_point[1]*math.sin(angle) , temp_point[0]*math.sin(angle)+temp_point[1]*math.cos(angle))
    temp_point = temp_point[0]+centerPoint[0] , temp_point[1]+centerPoint[1]
    return temp_point

def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n