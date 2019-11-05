def process_images(parameters):
    import os
    import h5py
    import pyklb
    import nibabel
    import numpy as np
    from PIL import Image
    from scipy import interpolate
    from types import SimpleNamespace    
    from skimage.external import tifffile
    from pyspark.sql.session import SparkSession
    from .._tools.nii_image import nii_image

    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    p = SimpleNamespace(**parameters)
        
    volume_nameRDD = sc.parallelize(p.volume_names)
    for i_color in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'volume%d.hdf5'%(i_color))):
            continue
                                                                        
        dir_volume = os.path.join(p.dir_output, 'volumes', str(i_color))
        os.makedirs(dir_volume, exist_ok=True)
        def initial_processing(name_volume):
            fullname_original = os.path.join(dir_volume, name_volume+'_original.nii.gz')
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            if os.path.isfile(fullname_original) or os.path.isfile(fullname_aligned):
                return
            
            try:
                # load input images
                fullname_input = os.path.join(p.dir_input, name_volume+p.ext)
                if ('.tif' in p.ext) or ('.tiff' in p.ext):
                    try:
                        data_volume = tifffile.imread(fullname_input)
                    except:
                        img = Image.open(fullname_input)
                        data_volume = []
                        for i in range(img.n_frames):
                            img.seek(i)
                            data_volume.append(np.array(img).T)
                        data_volume = np.array(data_volume)
                elif ('.h5' in p.ext) or ('.hdf5' in p.ext):
                    with h5py.File(fullname_input, 'r') as file_handle:
                        data_volume = file_handle[list(file_handle.keys())[0]][()]
                elif ('.klb' in p.ext):
                    data_volume = pyklb.readfull(fullname_input)
                    data_volume = data_volume.transpose(0, 2, 1)
            
                if data_volume.ndim == 2:
                    data_volume = data_volume[None, :, :]
                data_volume = data_volume.transpose(2, 1, 0)
            
                # get dimensions
                lx, ly, lz = data_volume.shape
                                
                # split two-color images into two halves        
                if p.n_colors == 2:
                    # ensure that two-frames have even number of y-dim voxels
                    assert(ly % 2 == 0)
                    ly /= 2
                    if i_color == 0:
                        data_volume = data_volume[:, :ly, :]
                    elif i_color == 1:
                        data_volume = data_volume[:, ly:, :]
                    
                # downsample in the x-y if specified
                if p.ds > 1:
                    if (lx % p.ds) or (ly % p.ds):
                        lx -= (lx % p.ds)
                        ly -= (ly % p.ds)
                        data_volume = data_volume[:lx, :ly, :]
                    
                    # make grid for computing downsampled values
                    sx_ds = np.arange(0.5, lx, p.ds)
                    sy_ds = np.arange(0.5, ly, p.ds)
                    xy_grid_ds = np.dstack(np.meshgrid(sx_ds, sy_ds, indexing='ij'))
                    
                    # get downsampled image
                    data_volume_ds = np.zeros((len(sx_ds), len(sy_ds), lz))
                    for zi in np.arange(lz):
                        interpolation_fx = interpolate.RegularGridInterpolator(
                            (np.arange(lx), np.arange(ly)),
                            data_volume[:, :, zi],
                            method='linear'
                        )
                        data_volume_ds[:, :, zi] = interpolation_fx(xy_grid_ds)
                
                    data_volume = data_volume_ds
                                                    
                # save image as a nifti file
                nibabel.save(
                    nii_image(data_volume.astype('float32'), p.affine_mat),
                    (fullname_original if p.alignment else fullname_aligned)
                )
                                
            except Exception as msg:
                raise Exception('Processing error for image %s: %s.'%(name_volume, msg))
                
        volume_nameRDD.foreach(initial_processing)
