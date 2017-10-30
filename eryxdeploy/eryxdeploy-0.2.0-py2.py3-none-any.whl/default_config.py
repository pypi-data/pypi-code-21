from fabric.state import env

# Fabric settings
env.use_ssh_config = True

# Eryx deploy
env.confirm_before_run = True
env.allow_skipping_cmd = False

env.stacks = {}
