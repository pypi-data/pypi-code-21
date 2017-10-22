class FileTypes():
    def __init__(self):
        self.format_movies = ['aaf', '3gp', 'asf', 'avchd', 'avi', 'cam', 'dat', 'dsh', 'flv', 'm1v', 'm2v', 'fla', 'flr', 'sol', 'm4v', 'matroska', 'wrap', 'mng', 'quicktime', 'mpeg', 'mp4', 'mxf', 'roq', 'nsv', 'ogg', 'rm', 'svi', 'smi', 'swf', 'wmv', 'mkv', 'mov', 'mpg']
        self.format_documents = ['602', 'abw', 'acl', 'afp', 'ami', 'amigaguide', 'ans', 'asc', 'aww', 'ccf', 'csv', 'cwk', 'dbk', 'doc', 'docm', 'docx', 'dot', 'dotx', 'egt', 'epub', 'ezw', 'fdx', 'ftm', 'ftx', 'gdoc', 'html', 'hwp', 'hwpml', 'lwp', 'mbp', 'md', 'mcw', 'mobi', 'nb', 'nbp', 'odm', 'odt', 'ott', 'omm', 'pages', 'pap', 'pdax', 'pdf', 'rtf', 'quox', 'rpt', 'sdw', 'se', 'stw', 'sxw', 'tex', 'info', 'troff', 'txt', 'uof', 'uoml', 'via', 'wpd', 'wps', 'wpt', 'wrd', 'wrf', 'wri', 'xhtml', 'xml', 'xps', '123', 'ab2', 'ab3', 'aws', 'clf', 'cell', 'csv', 'gsheet', 'numbers', 'gnumeric', 'ods', 'ots', 'qpw', 'sdc', 'slk', 'stc', 'sxc', 'tab', 'txt', 'vc', 'wk1', 'wk3', 'wk4', 'wks', 'wks', 'wq1', 'xlk', 'xls', 'xlsb', 'xlsm', 'xlsx', 'xlr', 'xlt', 'xltm', 'xlw', 'nfo', 'db']
        self.format_pictures = ['ase', 'art', 'bmp', 'blp', 'cd5', 'cit', 'cpt', 'cr2', 'cut', 'dds', 'dib', 'djvu', 'egt', 'exif', 'gif', 'gpl', 'grf', 'icns', 'ico', 'iff', 'jng', 'jpeg', 'jpg', 'jp2', 'jps', 'lbm', 'max', 'miff', 'mng', 'msp', 'nitf', 'ota', 'pbm', 'pc1', 'pc2', 'pc3', 'pcf', 'pcx', 'pdn', 'pgm', 'pi1', 'pi2', 'pi3', 'pict', 'png', 'pnm', 'pns', 'ppm', 'psb', 'psd', 'psp', 'px', 'pxm', 'pxr', 'qfx', 'raw', 'rle', 'sct', 'sgi', 'tga', 'tiff', 'tif', 'vtf', 'xbm', 'xcf', 'xpm', 'ai', 'odg', 'svg']
        self.format_music = ['8svx', '16svx', 'aiff', 'au', 'bwf', 'cdda', 'raw', 'wav', 'flac', 'la', 'pac', 'm4a', 'ape', 'optimfrog', 'rka', 'shn', 'tta', 'wv', 'wma', 'brstm', 'ast', 'amr', 'mp2', 'mp3', 'spx', 'gsm', 'wma', 'aac', 'mpc', 'vqf', 'realaudio', 'ots', 'swa', 'vox', 'voc', 'dwd', 'smp', 'aup', 'band', 'cust', 'mid', 'mus', 'sib', 'sid', 'ly', 'gym', 'vgm', 'psf', 'nsf', 'mod', 'ptb', 's3m', 'xm', 'it', 'mt2', 'mng', 'psf', 'minipsf', '', '2sf', '', 'rmj', 'spc', 'niff', 'musicxml', 'txm', 'ym', 'jam', 'asf', 'mp1', 'mscz', 'mscz', '', 'asx', 'm3u', 'pls', 'ram', 'txt/no', 'xpl', 'xspf', 'zpl', 'als', 'aup', 'band', 'cel', 'cpr', 'cwp', 'drm', 'mmr', 'npr', 'omfi', 'ses', 'sfl', 'sng', 'stf', 'snd', 'syn', 'flp']

    def get_file_format(self, file_ext):
        if not file_ext:
            return 0

        if file_ext in self.format_documents:
            return 1
        elif file_ext in self.format_movies:
            return 2
        elif file_ext in self.format_music:
            return 3
        elif file_ext in self.format_pictures:
            return 4
        else:
            return 0
