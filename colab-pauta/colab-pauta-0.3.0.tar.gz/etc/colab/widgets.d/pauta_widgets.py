from colab.widgets.widget_manager import WidgetManager
from colab_pauta.widgets.home_section import PautaHomeSectionWidget
from colab_pauta.widgets.navigation_links import PautaNavigationLinksWidget


WidgetManager.register_widget('home_section', PautaHomeSectionWidget())
WidgetManager.register_widget('navigation_links',
                              PautaNavigationLinksWidget())
