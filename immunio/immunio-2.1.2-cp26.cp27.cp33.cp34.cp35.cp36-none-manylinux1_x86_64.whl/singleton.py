from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)


# Hold singleton copies of key objects for this app
_global_config = None
_global_plugin_manager = None
_global_agent = None


def do_setup():
    """
    Called automatically if you `import immunio.start`. Loads the agent
    config and does the MonkeyPatching. For supported Frameworks, the
    agent will be created and started automatically on the first request.
    """
    config = get_config()
    if not config.agent_enabled:
        # If agent is not enabled, do nothing
        return
    # Do MonkeyPatching
    get_plugin_manager()


def wrap_wsgi_app(app):
    """
    Helper function to create the global Agent instance, and use it to
    wrap the supplied WSGI app callable.
    """
    config = get_config()
    if not config.agent_enabled:
        # If agent is not enabled, just return the original app
        return app
    # Create the agent
    agent = get_agent()
    return agent.wrap_wsgi_app(app)


def run_hook(hook_name, meta):
    """
    Helper function to get reference to the global agent and call
    `run_hook`.
    """
    agent = get_agent()
    return agent.run_hook("immunio_api", hook_name, meta)


def get_config():
    """
    Load the Agent Config into a singleton.
    """
    from immunio.config import Config
    global _global_config

    if not _global_config:
        _global_config = Config()
    return _global_config


def get_plugin_manager():
    """
    Load PluginManager into a singleton and actually do the MonkeyPatching.
    """
    from immunio.plugin_manager import PluginManager
    global _global_plugin_manager

    if not _global_plugin_manager:
        config = get_config()
        _global_plugin_manager = PluginManager(config, get_agent_func=get_agent)
    return _global_plugin_manager


def get_agent(create_if_required=True):
    """
    Shortcut function for accessing a singleton agent.
    """
    # Import inside function to avoid circular import.
    from immunio import agent
    global _global_agent

    if not _global_agent and create_if_required:
        _global_agent = agent.Agent(get_config(), get_plugin_manager())
        _global_agent.start()
    return _global_agent


def start():
    """
    Manual function to create an agent and start it up. Returns
    a reference to the agent so it can be used in a call to
    `agent.wrap_wsgi_app(original_app)`.

    This is only required for frameworks where we don't automatically wrap
    the produced wsgi app. In most cases you should just
    `import immunio.start` at the top of your application entry file.
    """
    return get_agent()
