# Mapping for DJI Drone
# V1.6 by Bimathax
import PIL.Image
from PIL.ExifTags import TAGS, GPSTAGS
from os import listdir, path
from math import cos, pi, tan, atan, acos, sin
from matplotlib import pyplot



####### CONSTANT #######
picture_folder = "Data_test/11_tri_reduce"
result_name = "test21.jpeg"
"""----------------"""
altitude = 120 #m
picture_x_meter = None #m
picture_y_meter = None #m
cota_x = 5#12 # pixel/m
cota_y = 5#10 # pixel/m
"""----------------"""
Blur = False #True Or False
show_graph = True
verbose = 1 #LEVEL 0-1-2-3 (Nothing,Error and Major Info, Normal, All)
setting_file = False
"""----------------"""
picture_align_type = 1 #1=Horizontal ; 2=Vertical
picture_align = ["reduce_DJI_0412.JPG","reduce_DJI_0415.JPG"] 
picture_align_correction = [-1,1] #[X;Y]
angle = -55 #deg
########################

def get_exif(pic_folder,picture_name):
    img = PIL.Image.open(str(path.join(pic_folder,picture_name)))
    exif_data = img.getexif()
    GPSINFO_TAG = next(
        tag for tag, name in TAGS.items() if name == "GPSInfo"
    )
    gps_info = exif_data.get_ifd(GPSINFO_TAG)
    return gps_info, img.width, img.height #DMS {0: b'\x02\x03\x00\x00', 1: 'N', 2: (44.0, 21.0, 8), 3: 'E', 4: (5.0, 10.0, 9), 5: b'\x00', 6: 116.042}
    
def coordonate_to_decimal(degree,minute,second):
    #print(degree,minute,second)
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

    #print(lat1,long1)
    #print(lat2,long2)

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
        angle=atan(x/y)
        if x>=0 and y<=0:
            #Angle=-45 Ajoute 90 deg
            #print("Changement angle 1")
            angle=angle*-1+pi/2
        elif x<=0 and y<=0:
            #print("Changement angle 2")
            angle=angle*-1-pi/2
    else :
        x, y=center_pic[picture_align_name]
        #print(x,y)
        angle=(1/2*pi-atan(x/y))*-1
    return angle
    

def rotation_center(angle_rad, x, y):
    a=angle_rad
    new_x = cos(a)*(x-tan(a)*y)
    new_y = (y/cos(a)) + tan(a)*(cos(a)*(x-tan(a)*y))
    return new_x, new_y

def image_x_pronostic(altitude):
    """
    See Altitude Excel Regression Courbe
    y = 1,2852x
    R^2 = 0,9999
    """
    return 1.2852*altitude

def image_y_pronostic(altitude):
    """
    See Altitude Excel Regression Courbe
    y = 0,7722x
    R^2 = 0,9917
    """
    return 0.7722*altitude #metre au sol

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
    #print("Delta x:",delta_x,"\nDelta y:",delta_y)
    width = delta_x*cota_x + width_pic
    height = delta_y*cota_y + height_pic
    
    #Bottom Left POINT COORDONATE IN METER
    x=x_min-(1/2*width_pic)/cota_x
    y=y_min-(1/2*height_pic)/cota_y
    #print("BOTTOM LEFT (x,y) :",x,y)
    #print(y, y_min)
    
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

def picture_correction(rotate_pic,picture_align_correction):
    #Picture Align Correction = [x,y]
    result={}
    for picture in rotate_pic:
        ls = rotate_pic[picture]
        x = ls[0]*picture_align_correction[0]
        y = ls[1]*picture_align_correction[1]
        result[picture]=[x,y]
    return result

def setting_file_save(result_name,cota_x,cota_y,picture_x_meter,picture_y_meter,altitude):
    file=open(f"SETTING_{result_name}.txt","w")
    file.write(result_name + "\n")
    file.write(f"Altitude : {altitude}")
    file.write(f"Cota X : {cota_x}")
    file.write(f"Cota Y : {cota_y}")
    file.write(f"picture_x_meter : {picture_x_meter}")
    file.write(f"picture_y_meter : {picture_y_meter}")

def main(pic_folder,result_name,altitude,picture_x_meter,picture_y_meter,blur,show_graph,picture_align,picture_align_type,cota_x,cota_y,angle,verbose,setting_file,picture_align_correction):
    ls_pic=[]
    for i in listdir(pic_folder):
        if i[0]!=".":
            ls_pic.append(i)
    if verbose==3:
        print("--- Liste Image ---")
        print(ls_pic,"\n")
    
    gps_pic={} #long, lat
    meter_pic={} #x, y
    pic_width=0;pic_height=0;altitude_sea=0;nb_pic=0
    for i in ls_pic:
        if verbose==3 or verbose==2:
            print("\n--- Exif ---\n" + str(i))
        gps, pic_width, pic_height = get_exif(pic_folder,i)
        if verbose==3:
            print("GPS:",gps)
            print("X-Y:",pic_width,pic_height)
        
        altitude_sea+=gps[6]
        nb_pic+=1

        if gps[1]=="N": nb_lat=1
        else: nb_lat=-1
        if gps[3]=="E": nb_long=1
        else: nb_long=-1        
        
        lat=nb_lat*coordonate_to_decimal(gps[2][0],gps[2][1],gps[2][2])
        long=nb_long*coordonate_to_decimal(gps[4][0],gps[4][1],gps[4][2])
        gps_pic[i]=[long,lat]
        if verbose == 3:
            print("Latitude :",lat, "\nLongitude :",long)
        y, x = deg_to_meter(lat,long)
        if verbose == 3 or verbose == 2:
            print(f"--- Convertion in Meter ---\nLat : {y}\nLong : {x}")
        meter_pic[i]=[x,y]
    #Moyenne Altitude
    altitude_sea=int(altitude_sea/nb_pic)
    if verbose==3:
        print("\n--- Altitude ---")
        print("Sea :",altitude_sea)
        print("Vol :",altitude)
    if verbose>=1:
        print("\n--- Size Picture ---")
        print("Width pixel :",pic_width)
        print("Height pixel :",pic_height)

    if verbose>=3:
        print("\n--- GPS Dictionnary ---")
        print(gps_pic)
        print("\n--- Meter Dictionnary ---")
        print(meter_pic)
    
    if show_graph:
        graph_representation(meter_pic)

    for i in picture_align:
        if i not in meter_pic:
            if verbose>=1:
                print(">>> ERROR : Name from picture_align not find in the folder")
            exit(0)
    new_center_img_name=picture_align[0]
    if verbose>=2:
        print(f"\n--- Picture Center ---\nCenter name : {new_center_img_name}")
    
    #center_pic = {}
    center_pic=calibration_newcenter(new_center_img_name, meter_pic)
    if verbose>=3:
        print("\n--- Centered Pictures List ---")
        print(center_pic)

    if show_graph:
        graph_representation(center_pic)
    
    if verbose >= 2:
        print("\n--- Set Angle ---")
    
    rotate_pic={}
    if angle==None :
        angle=angle_prediction(center_pic, picture_align[1],picture_align_type)*180/pi
    if verbose>=1:
        print(f"\n--- Angle ---\nDegre : {angle}")
    angle=angle*pi/180
    if verbose>=1:
        print("Radian :",angle)
    
    if verbose >= 2:
        print("\n--- Rotate Picture New Coordonates ---")
    for i in center_pic:
        x, y=center_pic[i]
        new_x, new_y = rotation_center(angle,x,y)
        rotate_pic[i] = [new_x, new_y]
    if verbose>=3:
        print(rotate_pic)
    if show_graph:
        graph_representation(rotate_pic)
    
    if verbose>=2:
        print("\n--- Alignement Correction ---")
    new_rotate_pic=picture_correction(rotate_pic,picture_align_correction)
    if verbose>=3:
        print(new_rotate_pic)
    rotate_pic={}
    rotate_pic=new_rotate_pic
    if show_graph:
        graph_representation(rotate_pic) #= new_rotate_pic
    
    #https://pixspy.com/
    #COTA X
    if verbose>=1:
        print("\n--- Cota X ---")
    if cota_x==None:
        if picture_x_meter==None:
            if verbose>=2:
                print("By altitude")
            picture_x_meter=image_x_pronostic(altitude)
            if verbose>=3:
                print("Pixel Pic width :", pic_width)
                print("Picture x meter :",picture_x_meter)
            cota_x = int(pic_width/picture_x_meter)
        else:
            if verbose>=2:
                print("By Picture_x_meter")
                cota_x = int(pic_width/picture_x_meter)
    else:
        if verbose>=2:
            print("By variable (already def)")
        cota_x=int(cota_x)
    if verbose>=1:
        print("Cota X :",cota_x)
    
    #COTA Y
    if verbose>=1:
        print("\n--- Cota Y ---")
    if cota_y==None:
        if picture_y_meter==None:
            if verbose>=2:
                print("By altitude")
            picture_y_meter=image_y_pronostic(altitude)
            if verbose>=3:
                print("Pixel Pic Height :", pic_height)
                print("picture y meter",picture_y_meter)
            cota_y = int(pic_height/picture_y_meter)
        else:
            if verbose>=2:
                print("By Picture_y_meter")
            cota_y = int(pic_height/picture_y_meter)
    else:
        if verbose>=2:
            print("By variable (already def)")
        cota_y = int(cota_y)
    if verbose>=1:
        print("Cota Y :",cota_y)
    
    
    width, height, bottom_left=final_picture_size(rotate_pic,pic_height,pic_width,cota_x,cota_y) #Cota px par m
    if verbose>=2:
        print(f"--- Final Size ---\nPixel X : {width}\nPixel Y : {height}\nBottom_Left_Corner in meter : {bottom_left}")

    if verbose>=2:
        print("\n--- Find Pixel Position ---")
    
    beginpixel_pic = {}
    for i in rotate_pic:
        middle_x, middle_y = rotate_pic[i]
        beginpixel_pic[i] = find_beginning_top_left_pixel(middle_x,middle_y,cota_x,cota_y,bottom_left[0],bottom_left[1],pic_width,pic_height)

    if verbose>=3:
        print(beginpixel_pic)
    if show_graph:
        graph_representation(beginpixel_pic)

    if verbose>=1:
        print("\n--- Result Creation ---")
    
    result = PIL.Image.new(mode="RGB", size=(width, height))
    for i in beginpixel_pic:
        try:
            if verbose>=1:
                print("Add :",i)
            result = copier_image(pic_folder,i,beginpixel_pic[i][0],beginpixel_pic[i][1],result,blur)
            if verbose>=3:
                print("Added !")
        except:
            if verbose>=1:
                print(">>> ERROR : With the add of the image",i)
            if verbose>=2:
                print(f"beginpx {beginpixel_pic[i]} size all (x-y) {width} {height} size litte {pic_width} {pic_height}")
    #result.putpixel((30,30),(0,255,255))
    ok=True
    try:
        result.save(result_name,"JPEG")
    except:
        ok=False
        if verbose>=1:
            print(">>> Error : Can't save the picture",result_name)
    if verbose>=1 and ok:
        print("Save AS :",result_name)
    result.show()
    if ok and setting_file:
        setting_file_save(result_name,cota_x,cota_y,picture_x_meter,picture_y_meter,altitude)


main(picture_folder,result_name,altitude, picture_x_meter,picture_y_meter,Blur,show_graph,picture_align,picture_align_type,cota_x,cota_y,angle,verbose,setting_file,picture_align_correction)
