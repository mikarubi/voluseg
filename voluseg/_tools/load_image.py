def load_image(fullname_input, ext):
    '''load volume based on input name and extension'''
    
    import h5py
    import numpy as np
    try:
        from skimage.external import tifffile
    except:
        import tifffile
    try:
        import PIL
        import pyklb
    except:
        pass

    if ('.tif' in ext) or ('.tiff' in ext):
        try:
            volume_input = tifffile.imread(fullname_input)
        except:
            img = PIL.Image.open(fullname_input)
            volume_input = []
            for i in range(img.n_frames):
                img.seek(i)
                volume_input.append(np.array(img).T)
            volume_input = np.array(volume_input)
    elif ('.h5' in ext) or ('.hdf5' in ext):
        with h5py.File(fullname_input, 'r') as file_handle:
            volume_input = file_handle[list(file_handle.keys())[0]][()]
    elif ('.klb' in ext):
        volume_input = pyklb.readfull(fullname_input)
        volume_input = volume_input.transpose(0, 2, 1)
        
    return volume_input