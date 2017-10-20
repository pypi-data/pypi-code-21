from .util import config

def msg():
    from .i18ns import en, zh_CN
    lang = get_lang()
    if lang=='zh':
        lang='zh_CN'
    return eval('%s.getJSON()' % lang)

def get_lang(default_lang='zh_CN'):
    m = config.getConfigs(config.COMMON, ['locale'])
    if m and m.get('locale'):
        return m['locale']
    else:
        return default_lang

