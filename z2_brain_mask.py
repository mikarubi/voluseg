def z2():
    global thr_prob
    thr_prob0 = np.copy(thr_prob)
                
    for frame_i in range(imageframe_nmbr):
        if os.path.isfile(output_dir + 'brain_mask' + str(frame_i) + '.hdf5'):
            try:
                mask_reset = eval(input('Reset brain_mask? [0, no]; 1, yes. '))
            except SyntaxError:
                mask_reset = 0
            
            if not mask_reset:
                continue
                
                                
        # get image mean
        def get_img_hdf(name_i):
            image_filename = image_dir(name_i, frame_i) + 'image_aligned.hdf5'
            with h5py.File(image_filename, 'r') as file_handle:
                return file_handle['V3D'][()].T
        
        image_dims = get_img_hdf(image_names[0]).shape
        assert(np.allclose(image_dims, (lx//ds, ly//ds, lz)))
        
        class accum_param(pyspark.accumulators.AccumulatorParam):
            '''define accumulator class'''
    
            def zero(self, val0):
                return np.zeros(val0.shape, dtype='float32')
    
            def addInPlace(self, val1, val2):
                return val1 + val2
                            
        image_accumulator = \
            sc.accumulator(np.zeros(image_dims, dtype='float32'), accum_param())
                            
        sc.parallelize(image_names).foreach(
            lambda name_i: image_accumulator.add(get_img_hdf(name_i)))
                    
        image_mean = 1.0 * image_accumulator.value / lt
                
        # get medium and fine resolution peaks
        def medin_filt(img, ftp):
            return ndimage.filters.median_filter(img, footprint=ftp)

        image_peak      = image_mean > medin_filt(image_mean, cell_ball)
        image_peak_fine = image_mean > medin_filt(image_mean, cell_ball_fine)
        
        # compute power and probability
        Powr = np.log10(image_mean.ravel())[:, None]
        Powr = np.log10(np.random.permutation(image_mean.ravel())[:100000, None])
        gmm = mixture.GaussianMixture(n_components=2, max_iter=100, n_init=100).fit(Powr)
        Prob = gmm.predict_proba(Powr)
        Prob = Prob[:, np.argmax(Powr[np.argmax(Prob, 0)])]
        
        # get and save brain mask
        thr_prob = np.copy(thr_prob0)
        mask_flag = (thr_prob != 0)
        while 1:
            plt.figure(1, (12, 4))
            plt.subplot(121); _ = plt.hist(Powr, 100); plt.title('10^(Pixel power histogram)')
            plt.subplot(122); _ = plt.hist(Prob, 100); plt.title('Probability threshold')
            plt.show()
            
            if not thr_prob:
                try:
                    thr_prob = eval(input('Enter probability threshold [default 0.5]: '))
                except SyntaxError:
                    thr_prob = 0.5
                    
            thr_prob = np.ravel(thr_prob)
            if len(thr_prob) == 1:
                ix = np.argmin(np.abs(Prob - thr_prob))
                thr_mask = 10 ** Powr[ix][0]
                if np.isinf(thr_prob):
                    thr_mask = thr_prob
            elif len(thr_prob) == 2:
                thr_mask = thr_prob[1]
                thr_prob = thr_prob[0]
                print('Proceeding with fluorescence threshold of %f.' %thr_mask)
            else:
                continue
            
            # remove all disconnected components less than 5000 cubic microliters in size
            small_obj = np.round(5000 * (resn_x * ds * resn_y * ds * resn_z)).astype(int)
            brain_mask = (image_mean > thr_mask)
            brain_mask = morphology.remove_small_objects(brain_mask, small_obj)
            for i in range(lz):
                plt.figure(1, (12, 6))
                plt.subplot(121); plt.imshow((image_mean * (    brain_mask))[:, :, i].T, cmap='hot')
                plt.subplot(122); plt.imshow((image_peak * (1 + brain_mask))[:, :, i].T, cmap='hot')
                plt.show()

            if not mask_flag:
                try:
                    mask_flag = eval(input('Is thr_prob = %.4f (thr_mask = %.1f) accurate? [1, yes]; 0, no. ' %(thr_prob, thr_mask)))
                except SyntaxError:
                    mask_flag = 1
                    
            if not mask_flag:
                thr_prob = 0
            else:
                break
        
        plt.close('all')
        
        with h5py.File(output_dir + 'brain_mask' + str(frame_i) + '.hdf5', 'w') as file_handle:
            file_handle['brain_mask']      = brain_mask.T
            file_handle['image_mean']      = image_mean.T
            file_handle['image_peak']      = image_peak.T
            file_handle['image_peak_fine'] = image_peak_fine.T
            file_handle['thr_prob']        = thr_prob
            file_handle['thr_mask']        = thr_mask
            file_handle['background']      = np.median(image_mean[brain_mask==0])

z2()
