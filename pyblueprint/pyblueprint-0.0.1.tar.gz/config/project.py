"""
project definitions
"""

import pyclassifiers.values

project_github_username = 'veltzer'
project_name = 'pyblueprint'
# project_website = 'https://{project_github_username}.github.io/{project_name}'.format(**locals())
project_website = 'https://github.com/{project_github_username}/{project_name}'.format(**locals())
project_website_source = 'https://github.com/{project_github_username}/{project_name}'.format(**locals())
project_website_git = 'git://github.com/{project_github_username}/{project_name}.git'.format(**locals())
project_website_download_ppa = 'https://launchpanet/~mark-veltzer/+archive/ubuntu/ppa'
project_website_download_src = project_website_source
# project_paypal_donate_button_id='ASPRXR59H2NTQ'
# project_google_analytics_tracking_id='UA-56436979-1'
project_long_description = 'draw diagrams using python'
project_short_description = project_long_description
# keywords to put on html pages or for search, dont put the name of the project or my details
# as they will be added automatically...
project_keywords = [
    'svg',
    'diagram',
    'python',
    'inkscape',
]
project_license = 'MIT'
project_year_started = '2017'
project_description = project_short_description
project_platforms = [
    'python3',
]
project_classifiers = [
    pyclassifiers.values.DevelopmentStatus__4_Beta,
    pyclassifiers.values.Environment__Console,
    pyclassifiers.values.OperatingSystem__OSIndependent,
    pyclassifiers.values.ProgrammingLanguage__Python,
    pyclassifiers.values.ProgrammingLanguage__Python__3__Only,
    pyclassifiers.values.Topic__Utilities,
]
project_data_files = []
