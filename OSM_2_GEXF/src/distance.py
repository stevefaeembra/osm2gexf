'''
Vincenty formula calculation - a very accurate way of measuring distance
between two (lat,lon) points a short distance apart

Created on 26 Nov 2011
Ported to Python by Steven Kay, from original Javascript code by Chris Veness
http://www.movable-type.co.uk/scripts/latlong-vincenty.html

This script licenced under CC-BY
ported by steven kay, Aug 2011
@author: Steven Kay
'''

import math
import angle
NaN = -99999999999999999

def distVincenty(lat1, lon1, lat2, lon2):
    """
    Returns distance between two points in meters
    """
    a = 6378137
    b = 6356752.314245
    f = 1/298.257223563
    L = angle.toRad(lon2-lon1)
    U1 = math.atan((1-f) * math.tan(angle.toRad(lat1)))
    U2 = math.atan((1-f) * math.tan(angle.toRad(lat2)))
    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)
    _lambda = L
    lambdaP=0.0
    iterLimit = 100;
    cont=True
    while cont:
        sinLambda = math.sin(_lambda)
        cosLambda = math.cos(_lambda)
        sinSigma = math.sqrt((cosU2*sinLambda) * (cosU2*sinLambda) +  (cosU1*sinU2-sinU1*cosU2*cosLambda) * (cosU1*sinU2-sinU1*cosU2*cosLambda));
        if (sinSigma==0):
            return 0
        cosSigma = sinU1*sinU2 + cosU1*cosU2*cosLambda
        sigma = math.atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha*sinAlpha
        cos2SigmaM = cosSigma - 2*sinU1*sinU2/cosSqAlpha
        if (math.isnan(cos2SigmaM)):
            cos2SigmaM = 0
        C = f/16*cosSqAlpha*(4+f*(4-3*cosSqAlpha))
        lambdaP = _lambda
        _lambda = L + (1-C) * f * sinAlpha * (sigma + C*sinSigma*(cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))
        iterLimit=iterLimit-1
        cont = abs(_lambda-lambdaP) > 1e-12 and iterLimit>0
    if (iterLimit==0):
        return NaN
    uSq = cosSqAlpha * (a*a - b*b) / (b*b)
    A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
    B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
    deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)-B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
    s = b*A*(sigma-deltaSigma)
    return s
