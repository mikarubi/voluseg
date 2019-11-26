def mask_images(parameters):
    '''create intensity mask from the average registered image'''
    
    import os
    import h5py
    import nibabel
    import pyspark
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn import mixture
    from skimage import morphology
    from types import SimpleNamespace
    from pyspark.sql.session import SparkSession
    from scipy.ndimage.filters import median_filter
    from voluseg._tools.ball import ball
    
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    p = SimpleNamespace(**parameters)
    
    volume_nameRDD = sc.parallelize(p.volume_names)
    for color_i in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'volume%d.hdf5'%(color_i))):
            continue
        
        dir_volume = os.path.join(p.dir_output, 'volumes', str(color_i))
        dir_plot = os.path.join(p.dir_output, 'mask_plots', str(color_i))
        os.makedirs(dir_plot, exist_ok=True)
        
        def load_volume(name_volume):
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            fullname_aligned_hdf = fullname_aligned.replace('.nii.gz', '.hdf5')
            if os.path.isfile(fullname_aligned):
                return nibabel.load(fullname_aligned).get_data()
            elif os.path.isfile(fullname_aligned_hdf):
                with h5py.File(fullname_aligned_hdf, 'r') as file_handle:
                    return (file_handle['V3D'][()].T)
            else:
                raise Exception('%s or %s do not exist.'%(fullname_aligned, fullname_aligned_hdf))
            
        lx, ly, lz = load_volume(p.volume_names[0]).shape
        
        class accum_param(pyspark.accumulators.AccumulatorParam):
            '''define accumulator class'''
    
            def zero(self, val0):
                return np.zeros(val0.shape, dtype='float64')
    
            def addInPlace(self, val1, val2):
                return np.add(val1, val2, dtype='float64')
                            
        volume_accum = sc.accumulator(np.zeros((lx, ly, lz), dtype='float64'), accum_param())
        volume_nameRDD.foreach(lambda name_i: volume_accum.add(load_volume(name_i)))
        volume_mean = 1.0 * volume_accum.value / p.lt
                
        # get peaks by comparing to a median-smoothed volume
        ball_radi = ball(0.5 * p.diam_cell, p.affine_mat)[0]
        volume_peak = volume_mean > median_filter(volume_mean, footprint=ball_radi)
        
        # compute power and probability
        voxel_intensity = np.percentile(volume_mean, np.r_[5:95:0.001])[:, None]
        gmm = mixture.GaussianMixture(n_components=2, max_iter=100, n_init=100).fit(voxel_intensity)
        voxel_probability = gmm.predict_proba(voxel_intensity)
        voxel_probability = voxel_probability[:, np.argmax(voxel_intensity[np.argmax(voxel_probability, 0)])]
        
        # compute intensity threshold
        if (p.thr_mask > 0) and (p.thr_mask <= 1):
            thr_probability = p.thr_mask
            ix = np.argmin(np.abs(voxel_probability - thr_probability))
            thr_intensity = voxel_intensity[ix][0]
        elif p.thr_mask > 1:
            thr_intensity = p.thr_mask
            ix = np.argmin(np.abs(voxel_intensity - thr_intensity))
            thr_probability = voxel_probability[ix]
        else:
            thr_intensity = - np.inf
            thr_probability = 0
            
        print('using probability threshold of %f.'%(thr_probability))
        print('using intensity threshold of %f.'%(thr_intensity))
        
        # get and save brain mask
        fig = plt.figure(1, (18, 6))
        plt.subplot(131),
        _ = plt.hist(voxel_intensity, 100);
        plt.plot(thr_intensity, 0, '|', color='r', markersize=200)
        plt.xlabel('voxel intensity')
        plt.title('intensity histogram with threshold (red)')
        
        plt.subplot(132),
        _ = plt.hist(voxel_probability, 100);
        plt.plot(thr_probability, 0, '|', color='r', markersize=200)
        plt.xlabel('voxel probability')
        plt.title('probability histogram with threshold (red)')
       
        plt.subplot(133),
        plt.plot(voxel_intensity, voxel_probability, linewidth=3)
        plt.plot(thr_intensity, thr_probability, 'x', color='r', markersize=10)
        plt.xlabel('voxel intensity')
        plt.ylabel('voxel probability')
        plt.title('intensity-probability plot with threshold (red)')
        
        plt.savefig(os.path.join(dir_plot, 'histogram.png'))
        plt.close(fig)
                
        # remove all disconnected components less than 5000 cubic microliters in size
        rx, ry, rz, _ = np.diag(p.affine_mat)
        volume_mask = (volume_mean > thr_intensity).astype('bool')
        thr_size = np.round(5000 * rx * ry * rz).astype(int)
        volume_mask = morphology.remove_small_objects(volume_mask, thr_size)
        
        # compute background fluorescence
        background = np.median(volume_mean[volume_mask==0])
        
        # compute mean timeseries
        bvolume_mask = sc.broadcast(volume_mask)
        masked_mean = lambda name_i: np.mean(load_volume(name_i)[bvolume_mask.value], dtype='float64')
        timeseries_mean = np.array(volume_nameRDD.map(masked_mean).collect())
        
        # save brain mask figures
        for i in range(lz):
            fig = plt.figure(1, (18, 6))
            plt.subplot(131); 
            plt.imshow(volume_mean[:, :, i].T, vmin=voxel_intensity[0], vmax=voxel_intensity[-1])
            plt.title('volume intensity (plane %d)'%(i))
            
            plt.subplot(132)
            plt.imshow(volume_mask[:, :, i].T)
            plt.title('volume mask (plane %d)'%(i))
            
            plt.subplot(133)
            img = np.stack((volume_mean[:, :, i], volume_mask[:, :, i], volume_mask[:, :, i]), axis=2)
            img[:, :, 0] = (img[:, :,0] - voxel_intensity[0]) / (voxel_intensity[-1] - voxel_intensity[0])
            img[:, :, 0] = np.minimum(np.maximum(img[:, :, 0], 0), 1)
            plt.imshow(np.transpose(img, [1, 0, 2]))
            plt.title('volume mask/intensity overlay (plane %d)'%(i))
            
            plt.savefig(os.path.join(dir_plot, 'mask_z%03d.png'%(i)))
            plt.close(fig)
            
        with h5py.File(os.path.join(p.dir_output, 'volume%s.hdf5'%(color_i)), 'w') as file_handle:
            file_handle['volume_mask']     = volume_mask.T
            file_handle['volume_mean']     = volume_mean.T
            file_handle['volume_peak']     = volume_peak.T
            file_handle['timeseries_mean'] = timeseries_mean
            file_handle['thr_intensity']   = thr_intensity
            file_handle['thr_probability'] = thr_probability
            file_handle['background']      = background
            
        # convert nifti images to hdf5 files
        def nii2hdf(name_volume):
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            fullname_aligned_hdf = fullname_aligned.replace('.nii.gz', '.hdf5')
            
            if not os.path.isfile(fullname_aligned_hdf):
                with h5py.File(fullname_aligned_hdf, 'w') as file_handle:
                    volume_aligned = nibabel.load(fullname_aligned).get_data().T.astype('float32')
                    file_handle.create_dataset('V3D', data=volume_aligned, compression='gzip')
                try:
                    os.remove(fullname_aligned)
                except:
                    pass
                
        volume_nameRDD.foreach(nii2hdf)
