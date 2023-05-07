# Mapping for DJI Drone
# V0.1 by Bimathax
import PIL.Image
from PIL.ExifTags import TAGS, GPSTAGS
from os import listdir, path
from math import cos, pi, tan, atan, acos, sin
from matplotlib import pyplot



### CONSTANT ###
picture_folder = "pictures"
result_name = "test20_4_____ds4.jpeg" #-0.175 rad or -10.0267 deg
meter_by_pixel_nb = 1
altitude = 22 #m
picture_x_meter = None #m
picture_y_meter = None #m
Blur = False #True Or False
show_graph = False
picture_align_type = 1 #1=Horizontal ; 2=Vertical
picture_align = ["reduce_DJI_0220.JPG","reduce_DJI_0222.JPG"] 
################

def get_exif(pic_folder,picture_name):
    img = PIL.Image.open(str(path.join(pic_folder,picture_name)))
    exif_data = img.getexif()
    GPSINFO_TAG = next(
        tag for tag, name in TAGS.items() if name == "GPSInfo"
    )
    gps_info = exif_data.get_ifd(GPSINFO_TAG)
    return gps_info, img.width, img.height #DMS {0: b'\x02\x03\x00\x00', 1: 'N', 2: (44.0, 21.0, 40.8486), 3: 'E', 4: (5.0, 10.0, 1.465), 5: b'\x00', 6: 116.042}
    
def coordonate_to_decimal(degree,minute,second):
    print(degree,minute,second)
    result = float(degree)+float(minute)/60+float(second)/3600
    return result
    
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

def calibration_newcenter(center_name, meter_pic):
    x_ref, y_ref = meter_pic[center_name]
    result={}
    for i in meter_pic:
        x, y= meter_pic[i]
        x-=x_ref
        y-=y_ref
        result[i] = [x,y]
    return result

def angle_prediction(center_pic,picture_align_name,picture_align_type):
    if picture_align_type==1:
        x, y=center_pic[picture_align_name]
        print(x,y)
        angle=atan(x/y)-pi
    else :
        x, y=center_pic[picture_align_name]
        print(x,y)
        angle=(1/2*pi-atan(x/y))*-1
    return angle
    

def rotation_center(angle_rad, x, y):
    a=angle_rad
    new_x = cos(a)*(x-tan(a)*y)
    new_y = (y/cos(a)) + tan(a)*(cos(a)*(x-tan(a)*y))
    return new_x, new_y

def image_x_pronostic(altitude):
    """
    After calculation test (I found 1m high = 1,369863014m on ground in XView)
    I code this to help in the picture definition
    1m high = 100/73m
    """
    return altitude*1000/730

def image_y_pronostic(altitude):
    """
    1m high = 1,088m y
    1m high = 0.5*2250/1034
    """
    return altitude*1/2*2250/1134

def cota_pronostic_bysize(width,height,picture_x_meter,picture_y_meter):
    cota_x = width/picture_x_meter
    cota_y = height/picture_y_meter
    return cota_x, cota_y

def final_picture_size(rotate_pic,height_pic,width_pic, cota_x, cota_y):
    x_min=0
    x_max=0
    y_min=0
    y_max=0
    for i in rotate_pic:
        x,y = rotate_pic[i]
        if x>x_max:x_max=x
        if x<x_min:x_min=x
        if y>y_max:y_max=y
        if y<y_min:y_min=y
    #print("HERE",rotate_pic)
    delta_x = x_max-x_min
    delta_y = y_max-y_min
    print("Delta x:",delta_x,"\nDelta y:",delta_y)
    width = delta_x*cota_x + width_pic
    height = delta_y*cota_y + height_pic
    
    #Bottom Left POINT COORDONATE IN METER
    x=x_min-(1/2*width_pic)/cota_x
    y=y_min-(1/2*height_pic)/cota_y
    print("BOTTOM LEFT (x,y) :",x,y)
    print(y, y_min)
    
    return int(width+1), int(height+1), [x,y]

def graph_representation(dic):
    #dic={name:x;y}
    for name in dic:
        x=dic[name][0]
        y=dic[name][1]
        pyplot.plot(x, y, color='green', marker='o', linestyle='dashed', linewidth=2, markersize=12)
    pyplot.show()

def find_beginning_top_left_pixel(middle_x,middle_y,cota_x,cota_y,bottom_left_x,bottom_left_y,img_width,img_height):
    #Find space in meter between the bottom left and the current point
    delta_x = middle_x-bottom_left_x
    delta_y = middle_y-bottom_left_y

    #Conversion en pixel
    x_pixel = delta_x*cota_x
    y_pixel = delta_y*cota_y
    
    #Enlève la moitié de l'image (pour arriver dans le coin en haut)
    x_pixel=int(x_pixel-1/2*img_width)
    y_pixel=int(y_pixel+1/2*img_height)
    return x_pixel, y_pixel



def copier_image(pic_folder,picture_name,begin_x,begin_y,image_result,blur):
    original = PIL.Image.open(str(path.join(pic_folder,picture_name)))
    y=0;x=0
    begin_x=begin_x
    begin_y=image_result.size[1]-begin_y
    for y in range(original.size[1]):
        for x in range(original.size[0]):
            px=original.getpixel((x,y))
            if blur == False:
                image_result.putpixel((begin_x+x,begin_y+y),px)
            else:
                px_from = image_result.getpixel((begin_x+x,begin_y+y))
                if px_from == (0,0,0):
                    image_result.putpixel((begin_x+x,begin_y+y),px)
                else:
                    middle=(int(px[0]+px_from[0]/2),int(px[1]+px_from[1]/2),int(px[2]+px_from[2]/2))
                    image_result.putpixel((begin_x+x,begin_y+y),middle)
    return image_result

def main(pic_folder,result_name,altitude,picture_x_meter,picture_y_meter,blur,show_graph,picture_align,picture_align_type):
    ls_pic=listdir(pic_folder)
    print(ls_pic)
    gps_pic={} #long, lat
    meter_pic={} #x, y
    pic_width=0;pic_height=0;altitude_sea=0;nb_pic=0
    for i in ls_pic:
        print("GET EXIF:", i)
        gps, pic_width, pic_height = get_exif(pic_folder,i)
        altitude_sea+=gps[6]
        nb_pic+=1

        if gps[1]=="N": nb_lat=1
        else: nb_lat=-1
        if gps[3]=="E": nb_long=1
        else: nb_long=-1        
        
        lat=nb_lat*coordonate_to_decimal(gps[2][0],gps[2][1],gps[2][2])
        long=nb_long*coordonate_to_decimal(gps[4][0],gps[4][1],gps[4][2])
        gps_pic[i]=[long,lat]
        print(lat,long)
        y, x = deg_to_meter(lat,long)
        meter_pic[i]=[x,y]
    #Moyenne Altitude
    altitude_sea=int(altitude_sea/nb_pic)
    print("ALTITUDE MER",altitude_sea)
    print("ALTITUDE VOL",altitude)
    print("TAILLE PHOTO px(X-Y)",pic_width,pic_height)

    print(gps_pic)
    print(meter_pic)
    
    if show_graph:
        graph_representation(meter_pic)

    """
    new_center_img_name=None
    for i in meter_pic:
        new_center_img_name=i
        break
    """
    for i in picture_align:
        if i not in meter_pic:
            print("ERREUR Noms images pour alignements")
            exit(0)
    new_center_img_name=picture_align[0]
    print("IMG Center",new_center_img_name)
    
    center_pic=calibration_newcenter(new_center_img_name, meter_pic)
    print(center_pic)

    if show_graph:
        graph_representation(center_pic)
    
    rotate_pic={}
    angle=1.2992 #dg
    angle=angle_prediction(center_pic, picture_align[1],picture_align_type)*180/pi
    print('ANGLE:',angle)
    print("Voulez vous gardez cette angle prédit [O/valeur] :")
    ans=input("->").lower()
    if ans != "o":
        angle=float(ans)
        print("NEW ANGLE :",angle)
    angle=angle*pi/180
    print("ANGLE in radian",angle)
    
    #angle=1.3029183314941166
    for i in center_pic:
        x, y=center_pic[i]
        new_x, new_y = rotation_center(angle,x,y)
        rotate_pic[i] = [new_x, new_y]
    
    print(rotate_pic)
    if show_graph:
        graph_representation(rotate_pic)
    

    #### MINI 2 SPEC ####
    """ NO OPERATIONAL
    focal=4.49 #mm
    sensor_x=58.42 #mm
    sensor_x=25.4
    cota = cota_pronostic_byaltitude(focal,sensor_x,pic_width,altitude)
    print(cota)
    """
    
    #https://pixspy.com/
    if picture_x_meter==None:
        print("FIND IMAGE X Meter BY ALTITUDE")
        picture_x_meter=image_x_pronostic(altitude)
        picture_y_meter=image_y_pronostic(altitude)
        print("picture x meter",picture_x_meter)
    cota_x = int(pic_width/picture_x_meter)
    cota_y = int(pic_height/picture_y_meter)
    print("COTA X-Y",cota_x,cota_y)
    
    
    width, height, bottom_left=final_picture_size(rotate_pic,pic_height,pic_width,cota_x,cota_y) #Cota px par m
    print("FINAL SIZE X-Y BOTTOMLEFT",width, height, bottom_left)

    beginpixel_pic = {}
    for i in rotate_pic:
        middle_x, middle_y = rotate_pic[i]
        beginpixel_pic[i] = find_beginning_top_left_pixel(middle_x,middle_y,cota_x,cota_y,bottom_left[0],bottom_left[1],pic_width,pic_height)

    if show_graph:
        graph_representation(beginpixel_pic)
    result = PIL.Image.new(mode="RGB", size=(width, height))
    for i in beginpixel_pic:
        try:
            print("ADD",i)
            result = copier_image(pic_folder,i,beginpixel_pic[i][0],beginpixel_pic[i][1],result,blur)
            print("END")
        except:
            print("erreur img",i)
            print(f"beginpx {beginpixel_pic[i]} size all (x-y) {width} {height} size litte {pic_width} {pic_height}")
    #result.putpixel((30,30),(0,255,255))
    try:
        result.save(result_name,"JPEG")
    except:
        print("Erreur Save")
    print("Save AS :",result_name)
    result.show()



 

main(picture_folder,result_name,altitude, picture_x_meter,picture_y_meter,Blur,show_graph,picture_align,picture_align_type)