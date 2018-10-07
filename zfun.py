# pip.main(['install', 'nibabel'])
# pip.main(['install', 'pynrrd'])
# pip.main(['install', 'h5py'])
# pip.main(['install', 'scikit-image'])
# pip.main(['install', 'future'])

import os
import sys
import shutil
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as pp
import matplotlib.pyplot as plt

import nibabel
import nrrd
import h5py
try:
    import pyklb
except:
    pass
import time
import PIL.Image
import tempfile
import multiprocessing

from scipy import io, interpolate, linalg, stats, ndimage, signal, optimize, sparse
from sklearn import cluster, mixture, decomposition, externals
from skimage import morphology, measure, filters
from skimage.external import tifffile
import xml

from builtins import range, zip


def detrend_dynamic_baseline(timesers, poly_ordr=2, tau=600):
    '''estimation of dynamic baseline for input timeseries'''
    
    # poly_ordr  polynomial order for detrending
    # tau:           timescale constant for baseline estimation (in seconds)
    # freq_cutoff:   highpass cutoff frequency
    # freq_stack:    frequency of imaging a single stack (in Hz)
    
    # timeseries mean
    timesers_mean = timesers.mean()
    
    # length of interval of dynamic baseline time-scales
    ltau = (np.round(tau * freq_stack / 2) * 2 + 1).astype(int)
    
    # detrend with a low-order polynomial
    xtime = np.arange(timesers.shape[0])
    coefpoly = np.polyfit(xtime, timesers, poly_ordr)
    timesers -= np.polyval(coefpoly, xtime)
    timesers = np.concatenate((timesers[::-1], timesers, timesers[::-1]))
    
    # highpass filter
    nyquist = freq_stack / 2
    if (freq_cutoff > 1e-10) and (freq_cutoff < nyquist - 1e-10):
        f_rng = np.array([freq_cutoff, nyquist - 1e-10])
        krnl = signal.firwin(lt, f_rng / nyquist, pass_zero=False)
        timesers = signal.filtfilt(krnl, 1, timesers, padtype=None)
        
    # restore mean
    timesers = timesers - timesers.mean() + timesers_mean
    
    # compute dynamic baseline
    timesers_df = pd.DataFrame(timesers)
    baseline_df = timesers_df.rolling(ltau, min_periods=1, center=True).quantile(0.1)
    baseline_df = baseline_df.rolling(ltau, min_periods=1, center=True).mean()
    baseline = np.ravel(baseline_df)
    baseline += np.percentile(timesers - baseline, 1)
    assert(np.allclose(np.percentile(timesers - baseline, 1), 0))
    
    return(timesers[lt:2*lt], baseline[lt:2*lt])
    

def sparseness(W, dim=0):
    '''vector sparseness along specified dimension'''

    n = W.shape[dim]
    l2 = np.sqrt(np.sum(np.square(W), dim))           # l2-norm
    l1 =         np.sum(np.abs(   W), dim)            # l1-norm
    return (np.sqrt(n) - l1 / l2) / (np.sqrt(n) - 1)  # sparseness


def nii_image(data, affmat):
    '''convert to nifti image'''
    nii = nibabel.Nifti1Image(data, affmat)
    nii.header['qform_code'] = 2      # make codes consistent with ANTS
    nii.header['sform_code'] = 1      # 1 scanner, 2 aligned, 3 tlrc, 4 mni.
    return nii


def image_dir(image_name, frame_i):
    '''get image directory'''
    return output_dir + 'brain_images/' + str(frame_i) + '/' + image_name + '/'


def downsample_xy(image_data, interpolation_method='linear'):
    '''downsample in the x-y dimension'''

    lx_, ly_, lz_ = image_data.shape

    # grid for computing downsampled values
    # indexing='ij' turns MATLAB meshgrid equiv. into MATLAB ndgrid equiv.
    # functions for 2-3 dims use Cartesian indexing ((x,y) or MATLAB meshgrid)
    # functions for N dims use matrix indexing ((i,j) or MATLAB ndgrid)
    xy_grid_ds = np.dstack(
        np.meshgrid(
            np.arange(0.5, lx_, ds),
            np.arange(0.5, ly_, ds),
            indexing='ij'
        )
    )
    lx_ds = len(np.arange(0.5, lx_, ds))
    ly_ds = len(np.arange(0.5, ly_, ds))

    # get downsampled image
    image_data_ds = np.zeros((lx_ds, ly_ds, lz_))
    for zi in np.arange(lz_):
        interpolation_fx = interpolate.RegularGridInterpolator(
            (np.arange(lx_), np.arange(ly_)),
            image_data[:, :, zi],
            method=interpolation_method
        )
        image_data_ds[:, :, zi] = interpolation_fx(xy_grid_ds)

    return image_data_ds.astype(data_type)


def upsample_xy(image_data_ds, interpolation_method='linear'):
    '''upsample in the x-y dimension'''

    lx_ds, ly_ds, lz_ = image_data_ds.shape
    
    assert(lx == lx_ds * ds)
    assert(ly == ly_ds * ds)

    # grid for computing upsampled values
    # indexing='ij' turns MATLAB meshgrid equiv. into MATLAB ndgrid equiv.
    # functions for 2-3 dims use Cartesian indexing ((x,y) or MATLAB meshgrid)
    # functions for N dims use matrix indexing ((i,j) or MATLAB ndgrid)
    xy_grid = np.dstack(
        np.meshgrid(
            np.arange(lx),
            np.arange(ly),
            indexing='ij'
        )
    )

    # get upsampled image
    image_data = np.zeros((lx, ly, lz_))
    for zi in np.arange(lz_):
        interpolation_fx = interpolate.RegularGridInterpolator(
            (np.arange(0.5, lx, ds), np.arange(0.5, ly, ds)),
            image_data_ds[:, :, zi],
            method=interpolation_method,
            bounds_error=False,
            fill_value=None
        )
        image_data[:, :, zi] = interpolation_fx(xy_grid)

    return image_data.astype(data_type)


def pad_z(command, image_data):
    '''pad in the z dimension'''

    if command == 'pad':
        return np.lib.pad(
            image_data, ((0, 0), (0, 0), (lpad, lpad)),
            'constant', constant_values=(np.percentile(image_data, 1),)
        )
    elif command == 'depad':
        return image_data[:, :, lpad:lz + lpad]


def ants_registration(in_nii, ref_nii, out_nii, out_tform, tip, restrict=None, exe=True):
    '''ants registration'''

    lin_tform_params = ' '.join([
        '--metric MI[' + ref_nii + ',' + in_nii + ',1,32,Regular,0.25]',
        '--convergence [1000x500x250x125]',
        '--shrink-factors 12x8x4x2',
        '--smoothing-sigmas 4x3x2x1vox',
    ])
    syn_tform_params = ' '.join([
        '--metric CC[' + ref_nii + ',' + in_nii + ',1,4]',
        '--convergence [100x100x70x50x20]',
        '--shrink-factors 10x6x4x2x1',
        '--smoothing-sigmas 5x3x2x1x0vox',
    ])
    antsRegistration_call = ' '.join([
        ants_dir + '/antsRegistration',
        '--initial-moving-transform [' + ref_nii + ',' + in_nii + ',1]',
        '--output [' + out_tform + ',' + out_nii + ']',
        '--dimensionality 3',
        '--float 1',
        '--interpolation Linear',
        '--winsorize-image-intensities [0.005,0.995]',
        '--use-histogram-matching 0',
        ('--restrict-deformation ' + restrict if restrict else ''),
        ('--transform Translation[0.1] '      + lin_tform_params if 't' in tip else ''),
        ('--transform Rigid[0.1] '            + lin_tform_params if 'r' in tip else ''),
        ('--transform Similarity[0.1] '       + lin_tform_params if 'i' in tip else ''),
        ('--transform Affine[0.1] '           + lin_tform_params if 'a' in tip else ''),
        ('--transform SyN[0.1,3,0] '          + syn_tform_params if 's' in tip else ''),
        ('--transform BSplineSyN[0.1,26,0,3]' + syn_tform_params if 'b' in tip else '')
    ])
    if exe:
        os.system(antsRegistration_call)
    else:
        return(antsRegistration_call)


def ants_transformation(in_nii, ref_nii, out_nii, in_tform, interpolation='Linear'):
    '''application of ants transform'''

    antsTransformation_call = ' '.join([
        ants_dir + '/antsApplyTransforms',
        '--dimensionality 3',
        '--input', in_nii,
        '--reference-image', ref_nii,
        '--output', out_nii,
        '--interpolation', interpolation,
        '--transform', in_tform,
        '--float'
    ])
    os.system(antsTransformation_call)


###


def parse_info(xml_filename, stack_filename, imageframe_nmbr):
    ''' parse inputs from xml file '''

    resn_x = 0.406
    resn_y = 0.406
        
    with open(xml_filename, 'r') as file_handle:
        xml_str = file_handle.read()
    
    try:
        xml_tree = xml.etree.ElementTree.fromstring(xml_str)
    except xml.etree.ElementTree.ParseError:
        xml_tree = xml.etree.ElementTree.fromstring(xml_str.replace('&', ' '))

    for info in xml_tree.findall('info'):
        if list(info.attrib.keys())[0] == 'dimensions':
            dims = info.attrib['dimensions'].split('x')
            if len(dims) == 2:      # if two dimensions
                dims.append('1')    # define third dimensions to equal 1
        if list(info.attrib.keys())[0] == 'exposure_time':
            t_exposure = float(info.attrib['exposure_time'])
        if list(info.attrib.keys())[0] == 'z_step':
            resn_z = float(info.attrib['z_step'])

    lx, ly, lz = [int(l.split(',')[0]) for l in dims[:3]]
    
    # ensure that two-frames have even number of y-dim pixels
    assert((imageframe_nmbr == 1) or (ly % 2 == 0))
    
    ly = ly // imageframe_nmbr

    try:
        if 'Stack_frequency' in stack_filename:
            freq_stack = np.fromfile(stack_filename, sep='\n')[0] # Hz
        else:
            with open(stack_filename, 'r') as file_handle:
                times_stack = np.array(file_handle.read().split('\t'))[1:-1]
                freq_stack = 1.0 / np.mean(np.diff(times_stack.astype(float)))
    except:
        print(('Warning: cannot read from ' + stack_filename + '.'))
        freq_stack = np.nan

    return resn_x, resn_y, resn_z, lx, ly, lz, t_exposure, freq_stack


def get_ball(radi):
    ''' morphological cell balls and midpoints '''
    ball = np.ones((
            np.maximum(1, np.round(radi / (resn_x * ds)).astype(int) * 2 + 1),
            np.maximum(1, np.round(radi / (resn_y * ds)).astype(int) * 2 + 1),
            np.maximum(1, np.round(radi /  resn_z      ).astype(int) * 2 + 1)), dtype=int)

    ball_xyzm = (np.array(ball.shape) - 1) / 2
    for xi in range(ball.shape[0]):
        for yi in range(ball.shape[1]):
            for zi in range(ball.shape[2]):
                xyzi_diff = ([xi, yi, zi] - ball_xyzm) * [resn_x * ds, resn_y * ds, resn_z]
                ball[xi, yi, zi] = np.sqrt(np.sum(np.square(xyzi_diff))) <= radi

    return (ball, ball_xyzm)


####


def init_image_process(image_name, frame_i=0, image_proc=1):
    print((image_name + ': start'))

    # load original images
    if '.tif' in image_ext:
        try:
            image_data = tifffile.imread(input_dir + image_name + image_ext)
        except:
            img = PIL.Image.open(input_dir + image_name + image_ext)
            image_data = []
            for i in range(img.n_frames):
                img.seek(i)
                image_data.append(np.array(img).T)
            image_data = np.array(image_data)
    elif ('.stack.bz2' in image_ext) or ('.stack.gz' in image_ext):
        tempdir = tempfile.mkdtemp() + '/'
        if '.stack.bz2' in image_ext:
            unzip_cmd = 'bzcat '
        elif '.stack.gz' in image_ext:
            unzip_cmd = 'zcat '
        os.system(
            unzip_cmd + input_dir + image_name + image_ext + ' > ' + tempdir + 'img.stack')
        image_data = \
            np.fromfile(
                tempdir + 'img.stack', dtype='int16', count=-1, sep='')\
            .reshape((lz, ly * imageframe_nmbr, lx))
        os.system('rm ' + tempdir + 'img.stack; rmdir ' + tempdir)
    elif '.stack' in image_ext:
        image_data = \
            np.fromfile(
                input_dir + image_name + image_ext, dtype='int16', count=-1, sep='')\
            .reshape((lz, ly * imageframe_nmbr, lx))
    elif ('.h5' in image_ext) or ('.hdf5' in image_ext):
        with h5py.File(input_dir + image_name + image_ext, 'r') as file_handle:
            image_data = file_handle[list(file_handle.keys())[0]][()]
    elif ('.klb' in image_ext):
        image_data = pyklb.readfull(input_dir + image_name + image_ext)
        image_data = image_data.transpose(0, 2, 1)

    if image_data.ndim == 2:
        image_data = image_data[None, :, :]
    image_data = image_data.transpose(2, 1, 0).astype(data_type)

    if not image_proc:
        print('returning dimensions.')
        return image_data.shape

    # split two-color images into two halves        
    if imageframe_nmbr == 2:
        if frame_i == 0:
            image_data = image_data[:, :ly, :]
        elif frame_i == 1:
            image_data = image_data[:, ly:, :]
        
    # ensure original dimensions are even
    if ds > 1:
        if lx % 2: image_data = image_data[:-1, :, :]
        if ly % 2: image_data = image_data[:, :-1, :]

    # downsample in the x-y dimension and pad in the z dimension
    if ds > 1:
        image_data = downsample_xy(image_data)
    if lpad:
        image_data = pad_z('pad', image_data)

    # create image directory and save image as a nifti file
    os.system('mkdir -p ' + image_dir(image_name, frame_i))
    nibabel.save(
        nii_image(image_data.astype(data_type), niiaffmat),
        image_dir(image_name, frame_i) + 'image_original' + nii_ext
    )

    print((image_name + ': end'))
