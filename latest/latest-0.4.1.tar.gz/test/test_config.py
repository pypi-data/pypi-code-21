try:
    import configparser
except:
    import ConfigParser as configparser


def test_config(config):
    assert config.templates_dir == '~/.latest/templates/'
    assert config.pyexpr_entry == r'\{\$'
    assert config.pyexpr_exit == r'\$\}'
    assert config.env_entry == r'<<<'
    assert config.env_exit == r'>>>'


def test_non_existing_config(non_existing_config):
    assert non_existing_config.env_entry == r'\\begin\{latest\}'
