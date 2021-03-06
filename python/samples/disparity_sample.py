"""
Sample code to read an image and estimate the disparity
Parameters can be input by hand or predefinite ones will be used
----
@veresion v1.1 - Januar 2017
@author Luca Palmieri
"""
import disparity.disparity_methods as rtxmain
import plenopticIO.imgIO as imgIO
import argparse
import os
import json
import pdb
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Read an image and estimate disparity")
    parser.add_argument(dest='input_filename', nargs=1, help="Name of the lens config file")
    parser.add_argument('-o', dest='output_path', default='./')
    parser.add_argument('--coarse', default=False, action='store_true')
    parser.add_argument('-t', dest='technique', default='sad')
    parser.add_argument('-dmin', dest='min_disp', default='1')
    parser.add_argument('-dmax', dest='max_disp', default='9')
    parser.add_argument('-nd', dest='num_disp', default='16')
    parser.add_argument('-scene', dest='scene_type', default='real')
    parser.add_argument('-err', dest='error', default=False)
    
    args = parser.parse_args()

    if os.path.exists(args.output_path) is False:
        raise OSError('Path {0} does not exist'.format(args.output_path))
                          
    params = rtxmain.EvalParameters()
    params.filename = args.input_filename[0]
    params.coarse = args.coarse
    params.technique = args.technique
    params.method = 'real_lut'
    params.min_disp = args.min_disp
    params.max_disp = args.max_disp
    params.num_disp = args.num_disp
    params.scene_type = args.scene_type
    params.analyze_err = args.error
    
    full_name, nothing = params.filename.split('.xml')
    separate_names = full_name.split('/')
    pic_name = separate_names[len(separate_names)-1]
    
    I, disp, Dwta, Dgt, Dconf, Dcoarse, disparities, ncomp, disp_avg, new_offset, error_measurements = rtxmain.estimate_disp(params)

    disp_name = "{0}/{1}_disp_{2}_{3}_{4}_{5}.png".format(args.output_path, pic_name, params.method, disparities[0], disparities[-1], params.technique) 
    disp_name_col = "{0}/{1}_disp_col_{2}_{3}_{4}_{5}.png".format(args.output_path, pic_name, params.method, disparities[0], disparities[-1], params.technique) 
    gt_name = "{0}/{1}_gt_{2}_{3}_{4}_{5}.png".format(args.output_path, pic_name, params.method, disparities[0], disparities[-1], params.technique) 
    gt_name_col = "{0}/{1}_gt_col_{2}_{3}_{4}_{5}.png".format(args.output_path, pic_name, params.method, disparities[0], disparities[-1], params.technique) 

    plt.subplot(121)
    plt.title("Input Image")
    plt.imshow(I)
    plt.subplot(122)
    plt.title("Disparity Image")
    plt.imshow(disp, vmin=disparities[0], vmax=disparities[-1], cmap='jet')
    plt.show()
    
    if Dgt is not None:
        plt.imsave(gt_name, Dgt, vmin=np.min(Dgt), vmax=np.max(Dgt), cmap='gray')
        plt.imsave(gt_name_col, Dgt, vmin=np.min(Dgt), vmax=np.max(Dgt), cmap='jet')

    if error_measurements is not None:
        #save in a file the errors
        error_analysis = dict()
        error_analysis['avg_error'] = error_measurements[0]
        error_analysis['mask_error'] = error_measurements[1]
        error_analysis['mse_error'] = error_measurements[2]
        badPix1, badPix2, badPixGraph = error_measurements[3]
        error_analysis['badpix1_avg'] = np.mean(badPix1)
        error_analysis['badpix2_avg'] = np.mean(badPix2)
        plotting = np.mean(badPixGraph, axis=0)
        error_analysis['err_threshold'] = plotting.tolist()
        error_analysis['bumpiness'] = error_measurements[4]
        depth_disc, depth_smooth, badPix1Disc, badPix2Disc, badPix1Smooth, badPix2Smooth, badPixGraphDisc, badPixGraphSmooth = error_measurements[5]
        error_analysis['badpix1disc'] = np.mean(badPix1Disc)
        error_analysis['badpix1smooth'] = np.mean(badPix1Smooth)
        error_analysis['badpix2disc'] = np.mean(badPix2Disc)
        error_analysis['badpix2smooth'] = np.mean(badPix2Smooth)
        plottingdisc = np.mean(badPixGraphDisc, axis=0)
        error_analysis['err_thr_disc'] = plottingdisc.tolist()
        plottingsmth = np.mean(badPixGraphSmooth, axis=0)
        error_analysis['err_thr_smooth'] = plottingsmth.tolist()
        error_analysis['disc_err'] = depth_disc
        error_analysis['smooth_err'] = depth_smooth     
        err_ana_name = "{0}/{1}_error_analysis_{2}_{3}_{4}.json".format(args.output_path, pic_name, disparities[0], disparities[-1], params.technique) 
        err_ana_csv = "{0}/{1}_error_analysis_{2}_{3}_{4}.csv".format(args.output_path, pic_name, disparities[0], disparities[-1], params.technique) 
        err_arr_csv = "{0}/{1}_error_array_{2}_{3}_{4}.csv".format(args.output_path, pic_name, disparities[0], disparities[-1], params.technique)      
        imgIO.write_csv_file(error_analysis, err_ana_csv, params.technique)
        plotting_arrays = [plotting, plottingdisc, plottingsmth]
        imgIO.write_csv_array(plotting_arrays, err_arr_csv, params.technique)
    
    plt.imsave(disp_name, disp, vmin=disparities[0], vmax=disparities[-1], cmap='gray')
    plt.imsave(disp_name_col, disp, vmin=disparities[0], vmax=disparities[-1], cmap='jet')
