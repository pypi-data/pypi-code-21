import NodeDefender

def production():
    NodeDefender.app.config.from_object('factory.ProductionConfig')

def development():
    NodeDefender.app.config.from_object('factory.DevelopmentConfig')

def testing():
    NodeDefender.app.config.from_object('factory.TestingConfig')
