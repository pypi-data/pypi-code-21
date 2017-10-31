def test_datasets():
    import subprocess
    import os
    from os.path import exists
    repo_n='ms_datasets'
    datasets=[
              # 'Firnberg_et_al_2014',
              'Olson_et_al_2014',
              # 'Melnikov_et_al_2014',
              ]
    datasets_dh='%s' % (repo_n)
    if not exists(datasets_dh):
        subprocess.call('git clone https://github.com/rraadd88/%s.git' % (repo_n),shell=True)

    os.chdir('%s/analysis' % (repo_n))
    for prj_dh in datasets:
        print prj_dh
        if exists(prj_dh):
            subprocess.call('dms2dfe %s' % (prj_dh),shell=True)
        # break
# test_datasets()
    
