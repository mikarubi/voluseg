def parse_info(xml_filename, stack_filename, n_colors):
    ''' parse inputs from xml file '''

    res_x = 0.406
    res_y = 0.406
        
    with open(xml_filename, 'r') as file_handle:
        xml_str = file_handle.read()
    
    try:
        xml_tree = xml.etree.ElementTree.fromstring(xml_str)
    except xml.etree.ElementTree.ParseError:
        xml_tree = xml.etree.ElementTree.fromstring(xml_str.replace('&', ' '))

    for info in xml_tree.findall('info'):
        if list(info.attrib.keys())[0] == 'dimensions':
            dims = info.attrib['dimensions'].split('x')
            if len(dims) == 2:      # if two dimensions
                dims.append('1')    # define third dimensions to equal 1
        if list(info.attrib.keys())[0] == 'exposure_time':
            t_section = float(info.attrib['exposure_time']) / 1000
        if list(info.attrib.keys())[0] == 'z_step':
            res_z = float(info.attrib['z_step'])

    lx, ly, lz = [int(l.split(',')[0]) for l in dims[:3]]
    
    # ensure that two-frames have even number of y-dim voxels
    assert((n_colors == 1) or (ly % 2 == 0))
    
    ly = ly // n_colors

    try:
        if 'Stack_frequency' in stack_filename:
            f_volume = np.fromfile(stack_filename, sep='\n')[0] # Hz
        else:
            with open(stack_filename, 'r') as file_handle:
                times_stack = np.array(file_handle.read().split('\t'))[1:-1]
                f_volume = 1.0 / np.mean(np.diff(times_stack.astype(float)))
    except:
        print(('Warning: cannot read from ' + stack_filename + '.'))
        f_volume = np.nan

    return res_x, res_y, res_z, lx, ly, lz, t_section, f_volume
