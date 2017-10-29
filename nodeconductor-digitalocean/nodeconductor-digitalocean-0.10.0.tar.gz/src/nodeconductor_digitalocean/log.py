from nodeconductor.logging.loggers import AlertLogger, alert_logger, EventLogger, event_logger


class DigitalOceanAlertLogger(AlertLogger):
    settings = 'structure.ServiceSettings'

    class Meta:
        alert_types = ['token_is_read_only']


class DropletResizeEventLogger(EventLogger):
    droplet = 'nodeconductor_digitalocean.Droplet'
    size = 'nodeconductor_digitalocean.Size'

    class Meta:
        event_types = ('droplet_resize_scheduled',
                       'droplet_resize_succeeded')


alert_logger.register('digital_ocean', DigitalOceanAlertLogger)
event_logger.register('droplet_resize', DropletResizeEventLogger)
