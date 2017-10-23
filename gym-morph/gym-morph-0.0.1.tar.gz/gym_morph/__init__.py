from gym.envs.registration import register
from .env import SPECIES, TASK

for species in SPECIES:
    for task in TASK:
        name = '-'.join(['Morph', species, task, 'v0'])
        kwargs = dict(species=species, task=task)
        register(id=name, entry_point='gym_morph.env:MorphEnv', kwargs=kwargs,
                 max_episode_steps=1000)
