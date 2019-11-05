def mask_volume(parameters):
    import os
    import h5py
    import nibabel
    import pyspark
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import ndimage
    from sklearn import mixture
    from skimage import morphology
    from types import SimpleNamespace
    from pyspark.sql.session import SparkSession
    from .._tools.ball import ball
    
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    p = SimpleNamespace(**parameters)
    
    volume_nameRDD = sc.parallelize(p.volume_names)
    for i_color in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'volume%d.hdf5'%(i_color))):
            continue
        
        dir_volume = os.path.join(p.dir_output, 'volumes', str(i_color))
        dir_plot = os.path.join(p.dir_output, 'mask_plots', str(i_color))
        os.makedirs(dir_plot, exist_ok=True)
        
        def get_data(name_volume):
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            return nibabel.load(fullname_aligned).get_data()
            
        lx, ly, lz = get_data(p.volume_names[0]).shape
        
        class accum_param(pyspark.accumulators.AccumulatorParam):
            '''define accumulator class'''
    
            def zero(self, val0):
                return np.zeros(val0.shape, dtype='float64')
    
            def addInPlace(self, val1, val2):
                return val1 + val2
                            
        volume_accum = sc.accumulator(np.zeros((lx, ly, lz), dtype='float64'), accum_param())
        volume_nameRDD.foreach(lambda name_i: volume_accum.add(get_data(name_i)))
        volume_mean = 1.0 * volume_accum.value / p.lt
                
        # get medium and fine resolution peaks
        def medin_filt(img, ftp):
            return ndimage.filters.median_filter(img, footprint=ftp)

        ball_radi = ball(0.5 * p.diam_cell, p.affine_mat)[0]
        volume_peak = volume_mean > medin_filt(volume_mean, ball_radi)
        
        # compute power and probability
        power_voxel = np.log10(volume_mean.ravel())[:, None]
        power_voxel = np.log10(np.random.permutation(volume_mean.ravel())[:100000, None])
        gmm = mixture.GaussianMixture(n_components=2, max_iter=100, n_init=100).fit(power_voxel)
        prob_voxel = gmm.predict_proba(power_voxel)
        prob_voxel = prob_voxel[:, np.argmax(power_voxel[np.argmax(prob_voxel, 0)])]
        
        # get and save brain mask
        fig = plt.figure(1, (12, 6))
        plt.subplot(121); _ = plt.hist(power_voxel, 100); plt.title('10^(Pixel power histogram)')
        plt.subplot(122); _ = plt.hist(prob_voxel, 100); plt.title('Probability threshold')
        plt.savefig(os.path.join(dir_plot, 'histogram.png'))
        plt.close(fig)
        
        if (p.thr_mask > 0) and (p.thr_mask < 1):
            print('Proceeding with probability threshold of %f.'%(p.thr_mask))
            ix = np.argmin(np.abs(prob_voxel - p.thr_mask))
            thr_intensity = 10 ** power_voxel[ix][0]
        elif p.thr_mask > 1:
            print('Proceeding with intensity threshold of %f.'%(p.thr_mask))
            thr_intensity = p.thr_mask
        else:
            print('Proceeding without mask threshold.')
            thr_intensity = - np.inf
        
        # remove all disconnected components less than 5000 cubic microliters in size
        rx, ry, rz, _ = np.diag(p.affine_mat)
        volume_mask = (volume_mean > thr_intensity)
        thr_size = np.round(5000 * rx * ry * rz).astype(int)
        volume_mask = morphology.remove_small_objects(volume_mask, thr_size)
        
        # compute background fluorescence
        background = np.median(volume_mean[volume_mask==0])
        
        # save brain mask figures
        for i in range(lz):
            fig = plt.figure(1, (12, 6))
            plt.subplot(121); plt.imshow((volume_mean * (    volume_mask))[:, :, i].T, cmap='hot')
            plt.subplot(122); plt.imshow((volume_peak * (1 + volume_mask))[:, :, i].T, cmap='hot')
            plt.savefig(os.path.join(dir_plot, 'mask_z%03d.png'%(i)))
            plt.close(fig)
            
        with h5py.File(os.path.join(p.dir_output, 'volume%s.hdf5'%(i_color)), 'w') as file_handle:
            file_handle['volume_mask']   = volume_mask.T
            file_handle['volume_mean']   = volume_mean.T
            file_handle['volume_peak']   = volume_peak.T
            file_handle['background']    = background
            file_handle['power_voxel']   = power_voxel
            file_handle['prob_voxel']    = prob_voxel
            file_handle['thr_intensity'] = thr_intensity
            
        # convert nifti images to hdf5 files
        def nii2hdf(name_volume):
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            fullname_aligned_hdf = fullname_aligned.replace('.nii.gz', '.hdf5')
            
            if not os.path.isfile(fullname_aligned_hdf):
                with h5py.File(fullname_aligned_hdf, 'w') as file_handle:
                    file_handle['V3D'] = nibabel.load(fullname_aligned).get_data().T
                os.remove(fullname_aligned)
                
        volume_nameRDD.foreach(nii2hdf)
