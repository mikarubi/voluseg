def update():
    '''update package'''
    
    try:
        from pip._internal import main
    except:
        from pip import main
    
    main(['install', 'git+https://github.com/mikarubi/voluseg.git', '--upgrade'])