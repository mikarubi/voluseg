def mask_volumes(parameters):
    '''create intensity mask from the average registered volume'''

    import os
    import h5py
    import pyspark
    import numpy as np
    from scipy import stats
    from sklearn import mixture
    from skimage import morphology
    from types import SimpleNamespace
    from scipy.ndimage.filters import median_filter
    from voluseg._tools.ball import ball
    from voluseg._tools.constants import ali, hdf
    from voluseg._tools.load_volume import load_volume
    from voluseg._tools.clean_signal import clean_signal
    from voluseg._tools.evenly_parallelize import evenly_parallelize

    # set up spark
    from pyspark.sql.session import SparkSession
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext

    # set up matplotlib
    import warnings
    import matplotlib
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    p = SimpleNamespace(**parameters)

    # compute mean timeseries and ranked dff
    fullname_timemean = os.path.join(p.dir_output, 'mean_timeseries')
    volume_nameRDD = evenly_parallelize(p.volume_names)
    if not os.path.isfile(fullname_timemean+hdf):
        dff_rank = np.zeros(p.lt)
        mean_timeseries_raw = np.zeros((p.n_colors, p.lt))
        mean_timeseries = np.zeros((p.n_colors, p.lt))
        mean_baseline = np.zeros((p.n_colors, p.lt))
        for color_i in range(p.n_colors):
            dir_volume = os.path.join(p.dir_output, 'volumes', str(color_i))

            def mean_volume(tuple_name_volume):
                name_volume = tuple_name_volume[1]
                fullname_volume = os.path.join(dir_volume, name_volume)
                return np.mean(load_volume(fullname_volume+ali+hdf), dtype='float')

            mean_timeseries_raw[color_i] = volume_nameRDD.map(mean_volume).collect()
            time, base = clean_signal(parameters, mean_timeseries_raw[color_i])
            mean_timeseries[color_i], mean_baseline[color_i] = time, base
            dff_rank += stats.rankdata((time - base) / time)

        # get high delta-f/f timepoints
        if p.type_timepoints == 'custom':
            timepoints = p.timepoints
        else:
            nt = p.timepoints
            if not nt:
                timepoints = np.arange(p.lt)
            else:
                if p.type_timepoints == 'dff':
                    timepoints = np.sort(np.argsort(dff_rank)[::-1][:nt])
                elif p.type_timepoints == 'periodic':
                    timepoints = np.linspace(0, p.lt, nt, dtype='int', endpoint=False)

        with h5py.File(fullname_timemean+hdf, 'w') as file_handle:
            file_handle['mean_timeseries_raw'] = mean_timeseries_raw
            file_handle['mean_timeseries'] = mean_timeseries
            file_handle['mean_baseline'] = mean_baseline
            file_handle['timepoints'] = timepoints

    # load timepoints
    with h5py.File(fullname_timemean+hdf, 'r') as file_handle:
        timepoints = file_handle['timepoints'][()]

    for color_i in range(p.n_colors):
        fullname_volmean = os.path.join(p.dir_output, 'volume%d'%(color_i))
        if os.path.isfile(fullname_volmean+hdf):
            continue

        dir_volume = os.path.join(p.dir_output, 'volumes', str(color_i))
        dir_plot = os.path.join(p.dir_output, 'mask_plots', str(color_i))
        os.makedirs(dir_plot, exist_ok=True)

        fullname_volume = os.path.join(dir_volume, p.volume_names[0])
        lx, ly, lz = load_volume(fullname_volume+ali+hdf).T.shape

        class accum_param(pyspark.accumulators.AccumulatorParam):
            '''define accumulator class'''

            def zero(self, val0):
                return np.zeros(val0.shape, dtype='float')

            def addInPlace(self, val1, val2):
                if p.type_mask == 'max':
                    return np.maximum(val1, val2, dtype='float')
                else:
                    return np.add(val1, val2, dtype='float')

        # geometric mean
        volume_accum = sc.accumulator(np.zeros((lx, ly, lz)), accum_param())

        def add_volume(tuple_name_volume):
            name_volume = tuple_name_volume[1]
            fullname_volume = os.path.join(dir_volume, name_volume)
            volume = load_volume(fullname_volume+ali+hdf).T
            if p.type_mask == 'geomean':
                volume = np.log10(volume)
            volume_accum.add(volume)

        if p.parallel_volume:
            evenly_parallelize(p.volume_names[timepoints]).foreach(add_volume)
        else:
            for name_volume in p.volume_names[timepoints]:
                add_volume(([], name_volume))
        volume_mean = volume_accum.value
        if p.type_mask != 'max':
            volume_mean = volume_mean / len(timepoints)
        if p.type_mask == 'geomean':
            volume_mean = 10 ** volume_mean

        # get peaks by comparing to a median-smoothed volume
        ball_radi = ball(0.5 * p.diam_cell, p.affine_mat)[0]
        volume_peak = volume_mean >= median_filter(volume_mean, footprint=ball_radi)

        # compute power and probability
        voxel_intensity = np.percentile(volume_mean[volume_mean>0], np.r_[5:95:0.001])[:, None]
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
        _ = plt.hist(voxel_intensity, 100)
        plt.plot(thr_intensity, 0, '|', color='r', markersize=200)
        plt.xlabel('voxel intensity')
        plt.title('intensity histogram with threshold (red)')

        plt.subplot(132),
        _ = plt.hist(voxel_probability, 100)
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
        volume_mask = (volume_mean > thr_intensity).astype(bool)
        thr_size = np.round(5000 * rx * ry * rz).astype(int)
        volume_mask = morphology.remove_small_objects(volume_mask, thr_size)

        # compute background fluorescence
        background = np.median(volume_mean[volume_mask==0])

        # save brain mask figures
        for i in range(lz):
            fig = plt.figure(1, (18, 6))
            plt.subplot(131)
            plt.imshow(volume_mean[:, :, i].T, vmin=voxel_intensity[0], vmax=voxel_intensity[-1])
            plt.title('volume intensity (plane %d)'%(i))

            plt.subplot(132)
            plt.imshow(volume_mask[:, :, i].T)
            plt.title('volume mask (plane %d)'%(i))

            plt.subplot(133)
            img = np.stack((volume_mean[:, :, i], volume_mask[:, :, i], volume_mask[:, :, i]), axis=2)
            img[:, :, 0] = (img[:, :, 0] - voxel_intensity[0]) / (voxel_intensity[-1] - voxel_intensity[0])
            img[:, :, 0] = np.minimum(np.maximum(img[:, :, 0], 0), 1)
            plt.imshow(np.transpose(img, [1, 0, 2]))
            plt.title('volume mask/intensity overlay (plane %d)'%(i))

            plt.savefig(os.path.join(dir_plot, 'mask_z%03d.png'%(i)))
            plt.close(fig)

        with h5py.File(fullname_volmean+hdf, 'w') as file_handle:
            file_handle['volume_mask'] = volume_mask.T
            file_handle['volume_mean'] = volume_mean.T
            file_handle['volume_peak'] = volume_peak.T
            file_handle['thr_intensity'] = thr_intensity
            file_handle['thr_probability'] = thr_probability
            file_handle['background'] = background
