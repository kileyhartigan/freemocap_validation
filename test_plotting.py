import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path 
import socket
import pickle
from tqdm import tqdm
import cv2
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
import sys 

from io import BytesIO


this_computer_name = socket.gethostname()
print(this_computer_name)


if this_computer_name == 'DESKTOP-V3D343U':
    freemocap_validation_data_path = Path(r"I:\My Drive\HuMoN_Research_Lab\FreeMoCap_Stuff\FreeMoCap_Balance_Validation\data")
elif this_computer_name == 'DESKTOP-F5LCT4Q':
    freemocap_validation_data_path = Path(r"C:\Users\aaron\Documents\HumonLab\Spring2022\ValidationStudy\FreeMocap_Data")
    #freemocap_validation_data_path = Path(r'D:\freemocap2022\FreeMocap_Data')
else:
    freemocap_validation_data_path = Path(r"C:\Users\kiley\Documents\HumonLab\SampleFMC_Data\FreeMocap_Data-20220216T173514Z-001\FreeMocap_Data")


sessionID = 'session_SER_1_20_22' #name of the sessionID folder
this_freemocap_session_path = freemocap_validation_data_path / sessionID
this_freemocap_data_path = this_freemocap_session_path/'DataArrays'

totalCOM_data_path = this_freemocap_data_path / 'totalBodyCOM_frame_XYZ.npy'
segmentedCOM_data_path = this_freemocap_data_path / 'segmentedCOM_frame_joint_XYZ.npy'
mediapipe_data_path = this_freemocap_data_path/'mediaPipeSkel_3d_smoothed.npy'
mediapipeSkeleton_file_name = this_freemocap_data_path/'mediapipeSkelcoordinates_frame_segment_joint_XYZ.pkl'


totalCOM_frame_XYZ = np.load(totalCOM_data_path) #loads in the data as a numpy array

segmentedCOM_frame_joint_XYZ = np.load(segmentedCOM_data_path)

mediapipeSkel_fr_mar_dim = np.load(mediapipe_data_path) #loads in the data as a numpy array

open_file = open(mediapipeSkeleton_file_name, "rb")
mediapipeSkelcoordinates_frame_segment_joint_XYZ = pickle.load(open_file)
open_file.close()

num_pose_joints = 33 #number of pose joints tracked by mediapipe 




pose_joint_range = range(num_pose_joints)
#frame_range = range(first_frame,last_frame)

mediapipe_pose_data = mediapipeSkel_fr_mar_dim[:,0:num_pose_joints,:] #load just the pose joints into a data array, removing hands and face data 

num_frames = len(mediapipe_pose_data)

#num_frame_range = range(num_frames)

num_frame_range = range(2900,3500)

skel_x = mediapipe_pose_data[:,:,0]
skel_y = mediapipe_pose_data[:,:,1]
skel_z = mediapipe_pose_data[:,:,2]

mx = np.nanmean(skel_x[int(num_frames/2),:])
my = np.nanmean(skel_y[int(num_frames/2),:])
mz = np.nanmean(skel_z[int(num_frames/2),:])

figure = plt.figure()
ax_range = 1000
 
# plt.tight_layout()
ax = figure.add_subplot(111, projection = '3d')
# ax2 = figure.add_subplot(211)




def animate(frame,num_frames):

    if frame % 100 == 0:
        print("Currently on frame: {}".format(frame))

    goodframe_x = skel_x[frame,:]
    goodframe_y = skel_y[frame,:]
    goodframe_z = skel_z[frame,:]

    # left_heel_x = goodframe_x[30]
    # left_heel_z = goodframe_z[30]

    # left_toe_x = goodframe_x[32]
    # left_toe_z = goodframe_z[32]

    # right_heel_x = goodframe_x[29]
    # right_heel_z = goodframe_z[29]

    # right_toe_x = goodframe_x[31]
    # right_toe_z = goodframe_z[31]

    # left_foot_x,left_foot_z = [left_heel_x,left_toe_x], [left_heel_z,left_toe_z]
    # right_foot_x,right_foot_z = [right_heel_x,right_toe_x], [right_heel_z,right_toe_z]

    segment_COM_x = segmentedCOM_frame_joint_XYZ[frame,:,0]
    segment_COM_y = segmentedCOM_frame_joint_XYZ[frame,:,1]
    segment_COM_z = segmentedCOM_frame_joint_XYZ[frame,:,2]

    total_COM_x = totalCOM_frame_XYZ[frame,0]
    total_COM_y = totalCOM_frame_XYZ[frame,1]
    total_COM_z = totalCOM_frame_XYZ[frame,2]

    plot_frame_bones_XYZ = mediapipeSkelcoordinates_frame_segment_joint_XYZ[frame]
    ax.clear()
    #ax2.clear()
    #ax2.set_xlim([mx-ax_range, mx+ax_range])
    #ax2.set_ylim([mz-ax_range, mz+ax_range])
    ax.set_xlim([mx-ax_range, mx+ax_range])
    ax.set_ylim([my-ax_range, my+ax_range])
    ax.set_zlim([mz-ax_range, mz+ax_range])
    ax.view_init(elev=-70., azim=-60)

    for segment in plot_frame_bones_XYZ.keys():
        prox_joint = plot_frame_bones_XYZ[segment][0] 
        dist_joint = plot_frame_bones_XYZ[segment][1]
        
        bone_x,bone_y,bone_z = [prox_joint[0],dist_joint[0]],[prox_joint[1],dist_joint[1]],[prox_joint[2],dist_joint[2]] 

        ax.plot(bone_x,bone_y,bone_z,color = 'black')
    
    ax.scatter(segment_COM_x,segment_COM_y,segment_COM_z, color = 'orange')    

    ax.scatter(total_COM_x,total_COM_y,total_COM_z, color = 'purple')
   

    ax.scatter(goodframe_x, goodframe_y,goodframe_z)

    #ax2.scatter(total_COM_x,total_COM_z, marker = '.', color = 'black', s = 5)
    #ax2.plot(left_foot_x,left_foot_z, color = 'red')
    #ax2.plot(right_foot_x,right_foot_z, color = 'blue')


ani = FuncAnimation(figure, animate, frames= num_frame_range, interval=(1/30)*100, repeat=False, fargs = (num_frames,))

writervideo = animation.FFMpegWriter(fps=30)
ani.save(this_freemocap_session_path/'test_with_trajectory.mp4', writer=writervideo)

#plt.show()



f=2