def z1():
    image_nameRDD = sc.parallelize(image_names)
    for frame_i in range(imageframe_nmbr):
                    
        image_nameRDD.foreach(lambda image_name: init_image_process(image_name, frame_i))
        
        def ants_reg(image_name):
            cmd = ants_registration(
                in_nii = image_dir(image_name, frame_i) + 'image_original' + nii_ext,
                ref_nii = image_dir(image_names[lt//2 - 1], frame_i) + 'image_original' + nii_ext,
                out_nii = image_dir(image_name, frame_i) + 'image_aligned' + nii_ext,
                out_tform = image_dir(image_name, frame_i) + 'alignment_tform_',
                tip = reg_tip,
                exe = False
            )
            flag = os.system(cmd)
            if flag:
                flag = os.system(cmd.replace(nii_ext + ',1]', nii_ext + ',0]'))
            if flag and lz==1:
                os.system(cmd.replace('--dimensionality 3', '--dimensionality 2'))
                out_nii = image_dir(image_name, frame_i) + 'image_aligned' + nii_ext
                image_data = nibabel.load(out_nii).get_data()
                nibabel.save(nii_image(image_data[:, :, None], niiaffmat), out_nii)
                
        image_nameRDD.foreach(ants_reg)
        
        # convert images to hdf5 format   
        def nii_to_hdf(image_name):        
            image_name_nii = image_dir(image_name, frame_i) + 'image_aligned' + nii_ext
            image_name_hdf = image_dir(image_name, frame_i) + 'image_aligned.hdf5'
    
            with h5py.File(image_name_hdf, 'w') as file_handle:
                image_data = nibabel.load(image_name_nii).get_data()
                image_data = pad_z('depad', image_data)
                file_handle['V3D'] = image_data.T
                
        image_nameRDD.foreach(nii_to_hdf)
            
        # delete images
        def delete_nii(image_name):
            os.remove(image_dir(image_name, frame_i) + 'image_original' + nii_ext)
            os.remove(image_dir(image_name, frame_i) + 'image_aligned' + nii_ext)
            
        image_nameRDD.foreach(delete_nii)

z1()
