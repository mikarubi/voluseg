def align_images(parameters):
    '''register images to a single middle image'''
    
    # do not run if registration is set to none
    if not parameters['registration']:
        return
    
    import os
    import shutil
    import nibabel
    from types import SimpleNamespace
    from pyspark.sql.session import SparkSession
    from voluseg._tools.nii_image import nii_image
    from voluseg._tools.ants_registration import ants_registration

    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    p = SimpleNamespace(**parameters)
    
    volume_nameRDD = sc.parallelize(p.volume_names)
    for color_i in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'volume%d.hdf5'%(color_i))):
            continue
                            
        dir_volume = os.path.join(p.dir_output, 'volumes', str(color_i))
        fullname_reference = os.path.join(dir_volume, 'reference_original.nii.gz')
        if not os.path.isfile(fullname_reference):
            fullname_lt_2 = os.path.join(dir_volume, p.volume_names[p.lt//2]+'_original.nii.gz')
            shutil.copyfile(fullname_lt_2, fullname_reference)
            
        dir_transform = os.path.join(p.dir_output, 'transforms', str(color_i))
        os.makedirs(dir_transform, exist_ok=True)        
        def register_volume(name_volume):
            os.environ['ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS'] = 1
            fullname_original = os.path.join(dir_volume, name_volume+'_original.nii.gz')
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            fullname_aligned_hdf = fullname_aligned.replace('.nii.gz', '.hdf5')
            if os.path.isfile(fullname_aligned) or os.path.isfile(fullname_aligned_hdf):
                return
            
            cmd = ants_registration(
                dir_ants = p.dir_ants,
                in_nii = fullname_original,
                ref_nii = fullname_reference,
                out_nii = fullname_aligned,
                out_tform = os.path.join(dir_transform, name_volume+'_tform_'),
                typ = {'rigid': 'r', 'translation': 't'}[p.registration]
            )
            flag = os.system(cmd)
            if flag:
                flag = os.system(cmd.replace('.nii.gz,1]', '.nii.gz,0]'))
            if flag and nibabel.load(fullname_original).shape[2]==1:
                os.system(cmd.replace('--dimensionality 3', '--dimensionality 2'))
                volume_input = nibabel.load(fullname_aligned).get_data()[:, :, None]
                nibabel.save(nii_image(volume_input, p.affine_mat), fullname_aligned)
                
            if os.path.isfile(fullname_aligned):
                os.remove(fullname_original)
            else:
                raise Exception('image %s not registered: flag %d.'%(name_volume, flag))
                                
        volume_nameRDD.foreach(register_volume)
        