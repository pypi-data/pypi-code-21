from thumbor.config import Config
Config.define('MONGO_LP_SERVER_HOST', 'localhost', 'MongoDB storage server host', 'MongoDB Storage')
Config.define('MONGO_LP_SERVER_PORT', 27017, 'MongoDB storage server port', 'MongoDB Storage')
Config.define('MONGO_LP_SERVER_DB', 'thumbor', 'MongoDB storage server database name', 'MongoDB Storage')
Config.define('MONGO_LP_SERVER_COLLECTION', 'images', 'MongoDB storage image collection', 'MongoDB Storage')
Config.define('MONGO_LP_DOC_FIELD', 'content', 'MongoDB document field used for image content', 'MongoDB Storage')
