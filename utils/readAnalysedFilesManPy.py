import scipy.io as sio
import numpy as np

import matplotlib.pyplot as plt
import itertools
class_wave = {0: 'Pacemaking', 1:'Colliding', 2:'Retrograde', 3:'Antegrade'}

def readManPyMatFile(filename, min_time, max_time, min_channel, max_channel):
    analysed_data = sio.loadmat(filename)
    predictions = analysed_data['marks']
    mask = analysed_data['mask'][0]
    labels = analysed_data['labels'][0]

    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    print('Estimated number of clusters: %d' % n_clusters_)

    scatter_points = np.where(predictions == 1)
    X = np.array(scatter_points).transpose()
    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    clustered_waves = {}
    idx = 0
    for k in unique_labels:
        if k == -1:
            continue
        class_member_mask = (labels == k)
        xy = X[class_member_mask]
        xy_arr = np.array(xy)
        #print(xy_arr)
        #print(np.where(xy_arr[:,1] > min_time))
        xy_arr = xy_arr[np.where((xy_arr[:,0] > min_channel) & (xy_arr[:,0] < max_channel))]
        xy_arr = xy_arr[np.where((xy_arr[:,1] > min_time) & (xy_arr[:,1] < max_time))]
        if(xy_arr.size):
            clustered_waves[idx] = np.array(xy_arr)
            idx+=1
    return clustered_waves

def readNiraMatFile(filename):
    analysed_data = sio.loadmat(filename)
    marked_data = analysed_data['data']['ManualMarksPos']
    grouped_data = marked_data[0][0][0][0][2][0]
    clustered_waves = {}
    for idx in range(0, grouped_data.shape[0]):
        clustered_waves[idx] = np.array(grouped_data[idx])
    print('Number of clustered cyclic waves:', len(clustered_waves))
    return clustered_waves

def readNiraMatActivationTimes(filename, min_time, max_time, min_channel, max_channel):
    analysed_data = sio.loadmat(filename)
    marked_data = analysed_data['data']['ManualMarksPos']
    marked_data = marked_data[0][0][0][0][1][0]
    idx = 1
    channel_time = []
    for array in marked_data:
        for times in array[0]:
            if ((idx > min_channel) & (idx < max_channel) & (times > min_time) & (times < max_time)):
                #print(idx, times)
                channel_time.append([idx, times])
        idx+=1
    return np.array(channel_time)

def readSignalPlots(filename, min_time, max_time, min_channel, max_channel):
    read_data = sio.loadmat(filename)
    data = np.array(read_data['data']['sig'][0][0])
    print(data.shape)
    return(data[min_channel - 1 : max_channel -1, min_time:max_time])

def readNiraMatWaves(filename, min_time, max_time, min_channel, max_channel):
    analysed_data = sio.loadmat(filename)
    marked_data = analysed_data['data']['Grouped']

    grouped_data = marked_data[0][0][0][0][1][0]
    clustered_waves = {}
    for idx in range(0, grouped_data.shape[0]):
        if((np.min(grouped_data[idx][:, 1]) > min_time) & (np.max(grouped_data[idx][:, 1]) < max_time)):
            clustered_waves[idx] = np.array(grouped_data[idx][:, :-1])
    print('Number of clustered cyclic waves:', len(clustered_waves))
    return clustered_waves

def consolidateActivationPoints(waves):
    array = waves[1]
    for key in waves.keys()[2:]:
        array = np.vstack((array, waves[key]))
    return array

def characteriseWaves(waves):
    #initilise all the variables storing the counts
    retrograde = 0
    antegrade =0
    idx = 0
    wave_metrics = {}

    wave_class = {}
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for key in waves.keys()[1:]:
        array = waves[key]
        z = np.polyfit(array[:,0], array[:, 1], 1)
        f = np.poly1d(z)
        x_new = np.linspace(np.min(array[:, 0]), np.max(array[:, 0]), 10)
        y_new = f(x_new)

        # reject groups that are grouped for 3 channels or less
        if(np.max(array[:,0]) - np.min(array[:,0]) < 4):
            continue

        slope = (y_new[-1] - y_new[0])/(x_new[-1] - x_new[0])
        if (slope < 0):
            retrograde+=1
            wave_class[key] = 0
        elif (slope > 0):
            antegrade+=1
            wave_class[key] = 1
        else:
            # reject group that are Instantaneuous
            print('Instantaneuous wave')
            continue

        ax1.scatter(array[:,1] , (array[:, 0]), s=20, c='b', marker="s")
        ax1.plot(y_new, x_new, c='r')
        plt.text(y_new[-1], x_new[-1], str(key))
        wave_metrics[key] = (wave_class[key], np.abs(1/slope), x_new[-1] - x_new[0])
        #print(wave_metrics[key])

    #plt.legend(loc='lower right')
    #plt.show()
    print('Antegrade', antegrade, 'Retrograde', retrograde)
    return wave_metrics

def evaluateTPFPFN(manual_marks, evaluated_marks, tol_win):
    unique_channels = np.unique(manual_marks[:, 0])
    TP = 0
    FP = 0
    FN = 0
    TP_list = []
    for channel in unique_channels:
        tp_len = 0
        activation_points_manual = list(np.unique(manual_marks[np.where(manual_marks[:, 0] == channel), 1][0]))
        activation_points_py = list(np.unique(evaluated_marks[np.where(evaluated_marks[:, 0] == channel), 1][0]))
        for val in activation_points_manual:
            for eval_val in activation_points_py:
                if (val - tol_win) < eval_val < (val + tol_win):
                    TP+=1
                    tp_len+=1
                    TP_list.append([channel, eval_val, val])
                    continue
        FP = FP + len(activation_points_py) - tp_len
        FN = FN + len(activation_points_manual) - tp_len

    #print(unique_channels)
    #P = TP/(TP + FP)
    #R = TP/(TP + FN)
    #F1 = 2 * (P * R)/(P + R)
    print(TP, FP, FN)#, F1)
    return TP_list

if __name__ == '__main__':
    #
    # data = readSignalPlots('/home/ssat335/Desktop/event_analyser/utils/python_read_data/AM_20120731_ALL_markedData.mat',182200, 185200, 1, 70)
    # waves_matlab = readNiraMatWaves('/home/ssat335/Desktop/event_analyser/utils/matlab_package/AM_20120731_ALL_markedData.mat', 182200, 185200, 1, 70)
    # at_nira_package = readNiraMatActivationTimes('/home/ssat335/Desktop/event_analyser/utils/matlab_package/AM_20120731_ALL_markedData.mat', 182200, 185200, 1, 70)
    # waves_py = readManPyMatFile('/home/ssat335/Desktop/event_analyser/utils/python_package_cyclic/AM_20120731_ALL_markedDataanalysed_data_1.mat', 182200, 185200, 1, 70)
    # waves_manual = readNiraMatFile('/home/ssat335/Desktop/event_analyser/utils/manual_marks/AM_20120731_ALL_markedData_cyclicProp_v1.mat')
    # (r_min, r_max, c_min, c_max) = (182200, 185200, 1, 70)

    # data = readSignalPlots('/home/ssat335/Desktop/event_analyser/utils/python_read_data/CM_20120414_ALL_markedData.mat',125500, 127500, 1, 70)
    # waves_matlab = readNiraMatWaves('/home/ssat335/Desktop/event_analyser/utils/matlab_package/CM_20120414_ALL_markedData.mat', 125500, 127500, 1, 70)
    # at_nira_package = readNiraMatActivationTimes('/home/ssat335/Desktop/event_analyser/utils/matlab_package/CM_20120414_ALL_markedData.mat', 125500, 127500, 1, 70)
    # waves_py = readManPyMatFile('/home/ssat335/Desktop/event_analyser/utils/python_package_cyclic/CM_20120414_ALL_markedDataanalysed_data_1.mat', 125500, 127500, 1, 70)
    # waves_manual = readNiraMatFile('/home/ssat335/Desktop/event_analyser/utils/manual_marks/CM_20120414_ALL_markedData_cyclicProp_v1.mat')
    # (r_min, r_max, c_min, c_max) = (125500, 127500, 1, 70)

    # data = readSignalPlots('/home/ssat335/Desktop/event_analyser/utils/python_read_data/DP_20130326_ALL_markedData.mat',101500, 104500, 1, 70)
    # waves_matlab = readNiraMatWaves('/home/ssat335/Desktop/event_analyser/utils/matlab_package/DP_20130326_ALL_markedData.mat', 101500, 104500, 1, 70)
    # at_nira_package = readNiraMatActivationTimes('/home/ssat335/Desktop/event_analyser/utils/matlab_package/DP_20130326_ALL_markedData.mat', 101500, 104500, 1, 70)
    # waves_py = readManPyMatFile('/home/ssat335/Desktop/event_analyser/utils/python_package_cyclic/DP_20130326_ALL_markedDataanalysed_data_1.mat', 101500, 104500, 1, 70)
    # waves_manual = readNiraMatFile('/home/ssat335/Desktop/event_analyser/utils/manual_marks/DP_20130326_ALL_markedData_cyclicProp_v1.mat')
    # (r_min, r_max, c_min, c_max) = (101500, 104500, 1, 70)

    data = readSignalPlots('python_read_data/SM_20140520_ALL_markedData.mat',139700, 142200, 1, 72)
    waves_matlab = readNiraMatWaves('matlab_package/SM_20140520_ALL_markedData.mat', 139700, 142200, 1, 72)
    at_nira_package = readNiraMatActivationTimes('matlab_package/SM_20140520_ALL_markedData.mat', 139700, 142200, 1, 72)
    waves_py = readManPyMatFile('python_package_cyclic/SM_20140520_ALL_markedDataanalysed_data_1.mat', 139700, 142200, 1, 72)
    waves_manual = readNiraMatFile('manual_marks/SM_20140520_ALL_markedData_cyclicProp_v1.mat')
    (r_min, r_max, c_min, c_max) = (139700, 142200, 1, 72)

    activation_points_py = consolidateActivationPoints(waves_py)
    activation_points_manual = consolidateActivationPoints(waves_manual)
    TP_matlab = np.array(evaluateTPFPFN(activation_points_manual, at_nira_package, 15))
    TP_python = np.array(evaluateTPFPFN(activation_points_manual, activation_points_py, 15))

    wave_class = characteriseWaves(waves_manual)
    wave_class = characteriseWaves(waves_py)
    wave_class = characteriseWaves(waves_matlab)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    #
    t = range(r_min,r_max)
    for idx in range(c_min, c_max):
        ax1.plot(t, data[idx - 1, :] + 100 * (idx + 1), color = 'b', lineWidth=0.2)
    ax1.scatter(TP_python[:,1] , (TP_python[:, 0] + 1) * 100, s=20, c='b', marker="s", label='True Prediction With Python')
    ax1.scatter(activation_points_manual[:,1], (activation_points_manual[:, 0]) * 100, s=10, c='r', marker="o", label='Manual')
    ax1.scatter(activation_points_py[:,1], (activation_points_py[:, 0] + 1) * 100, s=15, c='k', marker="o", label='Python Package')
    ax1.scatter(at_nira_package[:,1], (at_nira_package[:, 0] + 1) * 100, s=15, c='g', marker="o", label='Matlab Package')
    plt.legend(loc='lower right');
    plt.show()

    # fig = plt.figure()
    # ax1 = fig.add_subplot(111)
    # #
    # t = range(r_min,r_max)
    # for idx in range(c_min, c_max):
    #     ax1.plot(t, data[idx - 1, :] + 100 * (idx + 1), color = 'b', lineWidth=0.2)
    # ax1.scatter(at_nira_package[:,1], (at_nira_package[:, 0] + 1) * 100, s=10, c='b', marker="s", label='Matlab Package')
    # ax1.scatter(activation_points_manual[:,1], (activation_points_manual[:, 0]) * 100, s=10, c='r', marker="o", label='Manual')
    # ax1.scatter(activation_points_py[:,1], (activation_points_py[:, 0] + 1) * 100, s=15, c='k', marker="o", label='Python Package')
    # plt.legend(loc='lower right');
    # plt.show()
    #plt.savefig('SM_20140520_ALL_markedData.png')

    # plt.show()
