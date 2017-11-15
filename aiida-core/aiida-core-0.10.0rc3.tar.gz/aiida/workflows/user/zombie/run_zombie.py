
if __name__ == '__main__':
    from aiida.workflows.user.zombie.zombie import ZombieWorkChain
    from aiida.work.run import submit
    submit(ZombieWorkChain)


