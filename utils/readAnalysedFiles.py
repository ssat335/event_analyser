import scipy.io as sio
import numpy as np

import matplotlib.pyplot as plt
import itertools
class_wave = {0: 'Pacemaking', 1:'Colliding', 2:'Retrograde', 3:'Antegrade'}

def readNiraMatFile(filename):
    analysed_data = sio.loadmat(filename)
    marked_data = analysed_data['data']['ManualMarksPos']
    grouped_data = marked_data[0][0][0][0][2][0]
    clustered_waves = {}
    for idx in range(0, grouped_data.shape[0]):
        clustered_waves[idx] = np.array(grouped_data[idx])
    print('Number of clustered cyclic waves:', len(clustered_waves))
    return clustered_waves

def consolidateActivationPoints(waves):
    array = waves[1]
    for key in waves.keys()[2:]:
        array = np.vstack((array, waves[key]))
    return array

def characteriseWaves(waves):
    #initilise all the variables storing the counts
    pacemaking = 0
    colliding = 0
    retrograde = 0
    antegrade =0

    for key in waves.keys()[1:]:
        array = waves[key]
        wave_start_channel = np.min(array[:,0])
        wave_start_index = array[np.where(array[:,0] == wave_start_channel),1]
        wave_end_channel =  np.max(array[:,0])
        wave_end_index = array[np.where(array[:,0] == wave_end_channel),1]
        max_wave_index = np.max(array[:,1])
        min_wave_index = np.min(array[:,1])
        #print(wave_start_channel, wave_start_index, wave_end_channel, wave_end_index)
        wave_class = {}
        if (min_wave_index < wave_start_index and min_wave_index < wave_end_index):
            #print('Wave is Pacemaking')
            pacemaking+=1
        elif (max_wave_index > wave_start_index and max_wave_index > wave_end_index):
            #print('Wave is Colliding')
            colliding+=1
        elif wave_start_index < wave_end_index:
            #print('Wave is Retrograde')
            retrograde+=1
        else:
            #print('Wave is Antegrade')
            antegrade+=1

    print('Antegrade', antegrade, 'Retrograde', retrograde, 'Colliding', colliding, 'Pacemaking', pacemaking)
    return wave_class

if __name__ == '__main__':
    waves = readNiraMatFile('/home/ssat335/Desktop/event_analyser/utils/CM_20120414_ALL_markedData_cyclicProp.mat')
    activation_points = consolidateActivationPoints(waves)
    wave_class = characteriseWaves(waves)


    plt.scatter(activation_points[:,1], activation_points[:, 0])
    plt.show()
