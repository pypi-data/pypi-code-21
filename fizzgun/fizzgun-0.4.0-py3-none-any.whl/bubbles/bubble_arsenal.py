from fizzgun.application.dependencies import ModuleImporter, IdGenerator, StdoutWriter, RandomGenerator
from fizzgun.fizzgun_exception import FizzgunException


class BubbleArsenal(object):
    def __init__(self,
                 module_importer: ModuleImporter,
                 id_generator: IdGenerator,
                 random_generator: RandomGenerator,
                 stdout_writer: StdoutWriter):
        self._module_importer = module_importer
        self._id_generator = id_generator
        self._stdout_writer = stdout_writer
        self._random_generator = random_generator
        self._bubbles = []

    def add(self, bubble):
        self._bubbles.append(bubble)

    def bubbles(self):
        return self._bubbles

    def load_from_config(self, config):
        default_bubble_settings = config.get('default-settings', {})
        whitelist = config.get('tags-whitelist', [])
        blacklist = config.get('tags-blacklist', [])

        for bubble_pack_config in config['bubble-packs']:
            self._load_bubbles_module(bubble_pack_config,
                                      default_bubble_settings,
                                      filter_out=lambda bubble: self._filter_out(bubble, whitelist, blacklist))

    def _load_bubbles_module(self, bubble_pack_config, default_bubble_settings, filter_out):
        module_name = bubble_pack_config['module']
        bubbles_settings = bubble_pack_config.get('settings', {})

        bubbles = self._get_bubbles_from_package(module_name)

        for bubble_class in bubbles:
            if filter_out(bubble_class):
                continue
            self._construct_bubble(bubble_class, bubbles_settings, default_bubble_settings)

    def _get_bubbles_from_package(self, module_name):
        try:
            mod = self._module_importer.import_module(module_name)
        except Exception as e:
            raise FizzgunException("Unable to import bubble package '%s': %s" % (module_name, e), reason=e)

        if not hasattr(mod, 'BUBBLES'):
            raise FizzgunException("Bubble package '%s' has no 'BUBBLES' attribute" % module_name)

        return mod.BUBBLES

    def _construct_bubble(self, bubble_class, bubbles_settings, default_settings):
        self._stdout_writer.write("Loading bubble %s" % bubble_class.__name__)
        settings = default_settings.copy()
        settings.update(bubbles_settings.get(bubble_class.__name__, {}))

        bubble_instance = bubble_class(self._id_generator, self._random_generator, **settings)
        self.add(bubble_instance)

    @classmethod
    def _filter_out(cls, bubble_class, whitelist, blacklist):
        tags = getattr(bubble_class, 'TAGS', [])
        if whitelist and not any(t in whitelist for t in tags):
            return True
        if any(t in blacklist for t in tags):
            return True
        return False
