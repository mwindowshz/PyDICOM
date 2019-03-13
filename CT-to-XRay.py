"""

This example Loads DICOM CT Scan and creates Xray images from it
loading multiple files, sorting them by slice
location, building a 3D image and reslicing it in different planes.

"""

import pydicom
import numpy as np
import matplotlib.pyplot as plt
import sys
import glob

#helper funcitons
def PlotHistogram(d_volume,bins=20):
    plt.hist(d_volume.flatten(), bins=bins, color='c')
    plt.xlabel("Hounsfield Units (HU)")
    plt.ylabel("Frequency")
    plt.show()

'''HU units
     DICOM CT image has values in large ragne, our image has from -2000 - +4000
    the diffrent values, represent the absorbtion of xray waves in diffrent types of tissue
    air = -1000
    lung = -500
    fat = -100 to -50
    water = 0
    blood = +30 to +70
    Muscle = +10 to +40
    Liver = +40 to +60
    Bone = +700 (cancellous bone) to +3000 (cortical bone)
    '''
#first part creates bool matrix where value is above is true else is false , then we multiply with volume to get back a matrix where values below thresh are eliminated
def ThresholdImage(ThreeD_volume,thresh):
    vol_thresh = (ThreeD_volume > thresh ) * ThreeD_volume  
    return vol_thresh

def ThresholdBetween(ThreeD_volume,minVal,maxVal):
    vol_thresh = (ThreeD_volume > minVal ) * ThreeD_volume  
    vol_thresh = (vol_thresh < maxVal ) * vol_thresh
    return vol_thresh

def plotXray(volume):
    plt.imshow(np.mean(volume,axis=1),cmap='gray')
    plt.show()


#show sampels
def sample_overview(volume, rows=4, cols=4, start_with=10, show_every=3):
    fig,ax = plt.subplots(rows,cols,figsize=[12,12])
    for i in range(rows*cols):
        ind = start_with + i*show_every
        ax[int(i/rows),int(i % rows)].set_title('slice %d' % ind)
        ax[int(i/rows),int(i % rows)].imshow(volume[ind],cmap='gray')
        ax[int(i/rows),int(i % rows)].axis('off')
    plt.show()



def LoadDicomPath(path):
   
    # load the DICOM files
    files = []
    print('glob: {}'.format(path))
    for fname in glob.glob(path, recursive=False):
        print("loading: {}".format(fname))
        files.append(pydicom.read_file(fname))

    print("file count: {}".format(len(files)))

    # skip files with no SliceLocation (eg scout views)
    slices = []
    skipcount = 0
    for f in files:
        if hasattr(f, 'SliceLocation'):
            slices.append(f)
        else:
            skipcount = skipcount + 1
    if skipcount > 0 :
        print("skipped, no SliceLocation: {}".format(skipcount))

    # ensure they are in the correct order
    slices = sorted(slices, key=lambda s: s.SliceLocation)

    # pixel aspects, assuming all slices are the same
    ps = slices[0].PixelSpacing
    ss = slices[0].SliceThickness
    ax_aspect = ps[1]/ps[0]
    sag_aspect = ps[1]/ss
    cor_aspect = ss/ps[0]

    # create 3D array
    img_shape = list(slices[0].pixel_array.shape)
    img_shape.append(len(slices))
    # img3d = np.zeros(img_shape)
    volume = np.zeros([img_shape[2],img_shape[1],img_shape[0]])   # 225, 512 , 512  so we have 225 images with size of 512x512
    # fill 3D array with the images from the files
    for i, s in enumerate(slices):
        img2d = s.pixel_array
        # img3d[:, :, i] = img2d
        volume[i,:,:] = img2d

    return volume


''' main program code'''

dcomPath = 'D:/Learn/pydicom/Case2/*.dcm'
volume = LoadDicomPath(dcomPath)

PlotHistogram(volume)
#just to show our plots
sample_overview(volume)

#plotting diffrent cuts, where axis=1 is the xray image

fig, axs = plt.subplots(2, 2)
fig.suptitle('volume - 225,512,512')
axs[0, 0].imshow(np.mean(volume,axis=0),cmap='gray')
axs[0, 0].set_title('axis=0', fontsize=10)

####xray image is created by creating 2d image using mean on each colume of the 3d volume, createing a 2d representaion####
axs[0, 1].imshow(np.mean(volume,axis=1),cmap='gray')
axs[0, 1].set_title('axis=1 - xray image', fontsize=10)

axs[1, 0].imshow(np.mean(volume,axis=2),cmap='gray')
axs[1, 0].set_title('axis=2', fontsize=10)

plt.show()

#save first raw figure
plt.imshow(np.mean(volume,axis=1),cmap='gray')
plt.title("Raw xray before filtering")
plt.savefig('c:/temp/raw-xray.png')
plt.show()
#thresh hold the volume to see diffrent data in our create xray
#we choose diffrent parts of the HU data in the CT image

#first we go over a number
vol_thresh_500 = ThresholdImage(volume,500)
vol_thresh_1000 = ThresholdImage(volume,1000)
vol_thresh_1500 = ThresholdImage(volume,1500)
vol_thresh_2000 = ThresholdImage(volume,2000)

fig, axs = plt.subplots(2, 2)

axs[0, 0].imshow(np.mean(vol_thresh_500,axis=1),cmap='gray')
axs[0, 0].set_title('vol_thresh_500', fontsize=10)

axs[0, 1].imshow(np.mean(vol_thresh_1000,axis=1),cmap='gray')
axs[0, 1].set_title('vol_thresh_1000', fontsize=10)

axs[1, 0].imshow(np.mean(vol_thresh_1500,axis=1),cmap='gray')
axs[1, 0].set_title('vol_thresh_1500', fontsize=10)

axs[1, 1].imshow(np.mean(vol_thresh_2000,axis=1),cmap='gray')
axs[1, 1].set_title('vol_thresh_2000', fontsize=10)
plt.savefig('c:/temp/combinde thresh.png')
plt.show()

#now threshold between values:
vol_thresh_A = ThresholdBetween(volume,-10,10)
vol_thresh_B = ThresholdBetween(volume,30,70)
vol_thresh_C = ThresholdBetween(volume,100,400)
vol_thresh_D = ThresholdBetween(volume,400,800)

fig, axs = plt.subplots(2, 2)

axs[0, 0].imshow(np.mean(vol_thresh_A,axis=1),cmap='gray')
axs[0, 0].set_title('vol_thresh_-10 10', fontsize=10)

axs[0, 1].imshow(np.mean(vol_thresh_B,axis=1),cmap='gray')
axs[0, 1].set_title('vol_thresh_30 70', fontsize=10)

axs[1, 0].imshow(np.mean(vol_thresh_C,axis=1),cmap='gray')
axs[1, 0].set_title('vol_thresh_100 400', fontsize=10)

axs[1, 1].imshow(np.mean(vol_thresh_D,axis=1),cmap='gray')
axs[1, 1].set_title('vol_thresh_400 800', fontsize=10)
plt.savefig('c:/temp/combinde thresh 1.png')
plt.show()


#now threshold between values:
vol_thresh_A = ThresholdBetween(volume,800,1000)
vol_thresh_B = ThresholdBetween(volume,1000,1300)
vol_thresh_C = ThresholdBetween(volume,1300,1600)
vol_thresh_D = ThresholdBetween(volume,1600,2000)

fig, axs = plt.subplots(2, 2)

axs[0, 0].imshow(np.mean(vol_thresh_A,axis=1),cmap='gray')
axs[0, 0].set_title('vol_thresh_800 1000', fontsize=10)

axs[0, 1].imshow(np.mean(vol_thresh_B,axis=1),cmap='gray')
axs[0, 1].set_title('vol_thresh_1000 1300', fontsize=10)

axs[1, 0].imshow(np.mean(vol_thresh_C,axis=1),cmap='gray')
axs[1, 0].set_title('vol_thresh_1300 1600', fontsize=10)

axs[1, 1].imshow(np.mean(vol_thresh_D,axis=1),cmap='gray')
axs[1, 1].set_title('vol_thresh_1600 2000', fontsize=10)
plt.savefig('c:/temp/combinde thresh 2.png')
plt.show()



'''
dcomPath = 'D:/Learn/pydicom/Case2/*.dcm'
# load the DICOM files
files = []
print('glob: {}'.format(dcomPath))
for fname in glob.glob(dcomPath, recursive=False):
    print("loading: {}".format(fname))
    files.append(pydicom.read_file(fname))

print("file count: {}".format(len(files)))

# skip files with no SliceLocation (eg scout views)
slices = []
skipcount = 0
for f in files:
    if hasattr(f, 'SliceLocation'):
        slices.append(f)
    else:
        skipcount = skipcount + 1

print("skipped, no SliceLocation: {}".format(skipcount))

# ensure they are in the correct order
slices = sorted(slices, key=lambda s: s.SliceLocation)

# pixel aspects, assuming all slices are the same
ps = slices[0].PixelSpacing
ss = slices[0].SliceThickness
ax_aspect = ps[1]/ps[0]
sag_aspect = ps[1]/ss
cor_aspect = ss/ps[0]

# create 3D array
img_shape = list(slices[0].pixel_array.shape)
img_shape.append(len(slices))
# img3d = np.zeros(img_shape)
volume = np.zeros([img_shape[2],img_shape[1],img_shape[0]])   # 225, 512 , 512  so we have 225 images with size of 512x512
# fill 3D array with the images from the files
for i, s in enumerate(slices):
    img2d = s.pixel_array
    # img3d[:, :, i] = img2d
    volume[i,:,:] = img2d



plt.imsave('c:/temp/xray-gray.jpg',np.mean(volume,axis=1),cmap=plt.cm.bone)

plt.imsave('c:/temp/xray-gray2.jpg',np.mean(volume,axis=2),cmap=plt.cm.bone)

plt.imsave('c:/temp/xray2.jpg',np.mean(volume,axis=2))

plt.imsave('c:/temp/slice.jpg',(volume[0]))

plt.imsave('c:/temp/slice.jpg',(volume[220]))






print("slice thikness: {}".format(slices[0].SliceThickness))
print("pixel spacing (row,col) {} {}".format(slices[0].PixelSpacing[0],slices[0].PixelSpacing[0]))





    '''
    