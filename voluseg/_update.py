def update():
    '''update package'''
    
    import pip
    
    try:
        pip._internal.main(['install', 'git+https://github.com/mikarubi/voluseg.git', '--upgrade'])
    except:
        pip.main(['install', 'git+https://github.com/mikarubi/voluseg.git', '--upgrade'])
