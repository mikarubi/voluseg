def get_volume_name(fullname_volume, pi=None):
    '''get name of output volume (include name of plane if applicable)'''

    import os
    return os.path.basename(fullname_volume)+('_PLN'+str(pi).zfill(3) if pi else '')
