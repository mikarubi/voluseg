def load_metadata(parameters, filename_channel, filename_stack):
    '''fetch z-resolution, exposure time, and stack frequency'''

    import numpy as np
    from xml.etree import ElementTree

#    try:
    with open(filename_channel, 'r') as file_handle:
        xml_str = file_handle.read()
#    except:
#        print('error: cannot load %s.'%(filename_channel))

    try:
        xml_tree = ElementTree.fromstring(xml_str)
    except ElementTree.ParseError:
        xml_tree = ElementTree.fromstring(xml_str.replace('&', ' '))

    for info in xml_tree.findall('info'):
        if list(info.attrib.keys())[0] == 'exposure_time':
            t_section = float(info.attrib['exposure_time']) / 1000
            parameters['t_section'] = t_section
            print('fetched t_section.')
        if list(info.attrib.keys())[0] == 'z_step':
            res_z = float(info.attrib['z_step'])
            parameters['res_z'] = res_z
            print('fetched res_z.')

#    try:
    if 'Stack_frequency' in filename_stack:
        f_volume = np.fromfile(filename_stack, sep='\n')[0] # Hz
    else:
        with open(filename_stack, 'r') as file_handle:
            times_stack = np.array(file_handle.read().split('\t'))[1:-1]
            f_volume = 1.0 / np.mean(np.diff(times_stack.astype(float)))

    parameters['f_volume'] = f_volume
    print('fetched f_volume.')
#    except:
#        print('error: cannot load  %s.'%(filename_stack))

    return parameters
