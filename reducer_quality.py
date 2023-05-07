import PIL.Image
from os import listdir, path

### CONSTANT ###
picture_folder = "data_test/1"
compression_level=3
####

def reduce_quality(image):
    width=int(image.size[0]/2)
    height=int(image.size[1]/2)
    print(width, height)
    result=PIL.Image.new(mode="RGB",size=(width,height))
    y_final=0
    for y in range(0,image.size[1],2):
        x_final=0
        for x in range(0,image.size[0],2):
            nb=0;px=[]
            try:
                px.append(image.getpixel((x,y)))
                nb+=1
            except:pass
            try:
                px.append(image.getpixel((x+1,y)))
                nb+=1
            except:pass
            try:
                px.append(image.getpixel((x,y+1)))
                nb+=1
            except:pass
            try:
                px.append(image.getpixel((x+1,y+1)))
                nb+=1
            except:pass
            r=0;g=0;b=0
            for i in px:
                r+=i[0]
                g+=i[1]
                b+=i[2]
            r=int(r/nb)
            g=int(g/nb)
            b=int(b/nb)
            try:
                result.putpixel((x_final,y_final),(r,g,b))
            except:
                print(f"Erreur {x_final} {y_final}",end="\r")
            x_final+=1
        y_final+=1
    #result.show()
    return result

for picture in listdir(picture_folder):
    print("IMAGE :",picture)
    img=PIL.Image.open(str(path.join(picture_folder,picture)))
    exif = img.info['exif']
    for j in range(compression_level):
        print("LOOP",j)
        i = reduce_quality(img)
        img=i
    img.save(str(path.join(picture_folder,f"reduce_{picture}")),"JPEG",exif=exif)
print("END"," "*100)