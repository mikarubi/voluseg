def update():
    '''check for updates and update if updates are available'''
    
    import os
    from subprocess import run, PIPE
    
    dir_file = os.path.dirname(os.path.realpath(__file__))
    git_dir = '--git-dir=%s'%(os.path.join(dir_file, '.git'))
    work_tree = '--work-tree=%s'%(dir_file)
    
    try:
        output = run(['git', git_dir, work_tree, 'fetch', '--dry-run'], stdout=PIPE, stderr=PIPE)
        if output.stderr:
            response = input('voluseg is not up to date: update now? [y]/n: ')
            if not 'n' in response:                    
                try:
                    run(['git', git_dir, work_tree, 'pull'], stdout=PIPE, stderr=PIPE)
                    print('voluseg has successfully updated.')
                except Exception as msg:
                    print('voluseg has not updated: %s.'%(msg))
                
        else:
            print('voluseg is already up to date.')
    except Exception as msg:
        print('cannot check for voluseg updates: %s.'%(msg))
