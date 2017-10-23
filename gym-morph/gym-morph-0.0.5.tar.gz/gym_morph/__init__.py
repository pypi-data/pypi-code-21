from gym.envs.registration import register

# Based on the MuJoCo Ant model
SPECIES = ['longleg',  # morphing - extends first leg joint
           'longfoot',  # morphing - extends second leg joint
           'insect',  # non-morphing - 6 two-joint legs
           'lifter',  # non-morphing - extra lifing joint in hip
           'triple',  # non-morphing - three leg joints
           'ant']  # non-morphing - 4 two-joint legs

TASK = ['run',  # Run as fast as possible in a single direction
        'flagrun',  # Run to a specified 2d location
        'twister']  # Place foot on a specified spot


for species in SPECIES:
    for task in TASK:
        name = '-'.join(['Morph', species, task, 'v0'])
        kwargs = dict(species=species, task=task)
        register(id=name, entry_point='gym_morph.env:MorphEnv', kwargs=kwargs,
                 max_episode_steps=1000)
