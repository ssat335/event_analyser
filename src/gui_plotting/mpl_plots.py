import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt


from matplotlib.pyplot import cm
from matplotlib.font_manager import FontProperties

import matplotlib.mlab as mlab

import numpy as np


#user defined imports
import config_global as sp


newCmap = 'OrRd'#'Blues'
newCmap = 'gray'#'Blues'


def plot_2d_simple(inArr, title="", figSize=(6,6), filenameAndPath="", cbar=False, vMinVal=0, vMaxVal=1):
    print("In plot_2d_simple")
    global newCmap
    # fig = plt.figure()
    fig = plt.figure(figsize=figSize)



    print("After figure")

    # ax = fig.gca()
    ax = plt.axes()

    # plt.yticks([])
    # plt.xticks([])

    print("inArr.shape: ", inArr.shape)
    im = ax.imshow(inArr, cmap=newCmap, interpolation='nearest', vmin=vMinVal, vmax=vMaxVal)
    print("After imshow")


    if len(title) > 0:
        ax.set_title(title)

    ax.set_axis_off()
    # subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
    #             hspace = 0, wspace = 0)
    ax.margins(0,0)
    fig.tight_layout()

    # gca().xaxis.set_major_locator(NullLocator())
    # gca().yaxis.set_major_locator(NullLocator())   

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)     

    # plt.axis(im.get_extent())

    # ax.axis('tight')
    # ax.get_xaxis().set_visible(False)
    # ax.get_yaxis().set_visible(False)
    fig.subplots_adjust(left=0,right=1,bottom=0,top=1, hspace=0, wspace=0)

    if cbar:
        fig.colorbar(im, orientation='vertical')

    if len(filenameAndPath) > 0:
        fig.savefig(filenameAndPath, bbox_inches='tight', pad_inches=0)
    fig.show()
    print("End plot_2d_simple")


def plot_swImage_grid(swData, swLabels, linePlot=False, iTitle=""):

    swIndices = np.where(swLabels==1)
    nSlowWaves = len(swIndices[0])

    if linePlot :

        maxNimages = 800        

        pixelsPerRow = 14
        pixelsPerCol = 38
        nCols = 40

        gap = 4

        swData = (swData * (pixelsPerRow-gap-1))
        swData = np.trunc(swData)
        swData = swData.astype(int)

        # print("swData: ", swData[])

    else :

        maxNimages = 800

        pixelsPerRow = 7
        pixelsPerCol = 7
        nCols = 100

        gap = 1

    nRows = int(maxNimages / nCols)

    swImages = np.ones(shape=(int(pixelsPerRow * nRows),int(pixelsPerCol * nCols)), dtype=float)
    print("swImages.shape: ", swImages.shape)
    colI = 0
    rowI = 1
    imageI = 0

    for swI in swIndices[0]:

        imageI += 1
        colI += 1
        if colI == nCols:
            colI = 0
            rowI += 1

        rowStart = rowI * pixelsPerRow
        colStart = colI * pixelsPerCol

        try:
            if linePlot:

                unravelled = swData[swI,0,:,:].ravel()
                swImage = np.ones(shape=((pixelsPerRow-gap), (pixelsPerCol-gap)), dtype=int)

                for colInner in range(0, swImage.shape[1]) :
                    swImage[unravelled[colInner], colInner] = 0

                # Swap image to 2d plot


            else:
                swImage = swData[swI,0,:,:]

            swImages[rowStart : (rowStart + (pixelsPerRow-gap)), colStart : (colStart + (pixelsPerCol-gap))] = swImage

        except Exception as e:
            print(e)            
            print(swData[swI,0,:,:])

        if imageI >= maxNimages:
            print("ImageI ", imageI," >= maxNImages ",maxNimages)
            break
    
    return swImages


    


