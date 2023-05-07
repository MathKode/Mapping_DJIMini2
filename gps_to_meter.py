from math import acos, sin, cos, pi
lat1=0
long1=0

lat2=49.36126955555556
long2=6.167231805555556

def dg_to_rad(angle):
    return angle*pi/180

def haversine(lat1,long1,lat2,long2):
    #https://gps-coordinates.org/distance-between-coordinates.php
    #https://www.youtube.com/watch?v=HaGj0DjX8W8
    lat1=dg_to_rad(lat1)
    long1=dg_to_rad(long1)
    lat2=dg_to_rad(lat2)
    long2=dg_to_rad(long2)

    print(lat1,long1)
    print(lat2,long2)

    # Rayon moyen de la terre 6_371_005.076123 metres
    #d en mètre
    d=6_371_005.076123*acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(long1-long2))
    return d

def deg_to_meter(lat,long):
    #Par rapport aux méridien de greenwich et au 1 parrallelle
    x=haversine(lat,long,lat,0)
    y=haversine(lat,long,0,long)
    return x, y

deg_to_meter(lat2,long2)
print(haversine(lat1,long1,lat2,long2))
