def align_images(parameters):
    import os
    import shutil
    import nibabel
    from types import SimpleNamespace
    from pyspark.sql.session import SparkSession
    from .._tools.nii_image import nii_image
    from .._tools.ants_registration import ants_registration

    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    p = SimpleNamespace(**parameters)
    
    volume_nameRDD = sc.parallelize(p.volume_names)
    for i_color in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'volume%d.hdf5'%(i_color))):
            continue
                            
        dir_volume = os.path.join(p.dir_output, 'volumes', str(i_color))
        fullname_reference = os.path.join(dir_volume, 'reference_original.nii.gz')
        if not os.path.isfile(fullname_reference):
            fullname_lt_2 = os.path.join(dir_volume, p.volume_names[p.lt//2]+'_original.nii.gz')
            shutil.copyfile(fullname_lt_2, fullname_reference)
            
        dir_transform = os.path.join(dir_volume, 'transforms')
        os.makedirs(dir_transform, exist_ok=True)        
        def alignment(name_volume):
            fullname_original = os.path.join(dir_volume, name_volume+'_original.nii.gz')
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            if os.path.isfile(fullname_aligned):
                return
            
            if p.alignment:
                cmd = ants_registration(
                    dir_ants = p.dir_ants,
                    in_nii = fullname_original,
                    ref_nii = fullname_reference,
                    out_nii = fullname_aligned,
                    out_tform = os.path.join(dir_transform, name_volume+'_tform_'),
                    typ = {'rigid': 'r', 'translation': 't'}[p.alignment]
                )
                flag = os.system(cmd)
                if flag:
                    flag = os.system(cmd.replace('.nii.gz,1]', '.nii.gz,0]'))
                if flag and nibabel.load(fullname_original).shape[2]==1:
                    os.system(cmd.replace('--dimensionality 3', '--dimensionality 2'))
                    data_volume = nibabel.load(fullname_aligned).get_data()[:, :, None]
                    nibabel.save(nii_image(data_volume, p.affine_mat), fullname_aligned)
                if flag:
                    raise Exception('Registration error for image %s.'%(name_volume))
                    
                os.remove(fullname_original)
                                
        volume_nameRDD.foreach(alignment)
        