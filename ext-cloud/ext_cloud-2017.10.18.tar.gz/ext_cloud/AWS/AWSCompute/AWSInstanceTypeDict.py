"""
http://aws.amazon.com/ec2/instance-types/
"""
INSTANCE_TYPES = {
    't1.micro': {
        'id': 't1.micro',
        'name': 'Micro Instance',
        'cpus': 1,
        'ram': 0.613,
        'disk': 15,
        'bandwidth': None
    },
    'm1.small': {
        'id': 'm1.small',
        'name': 'Small Instance',
        'cpus': 1,
        'ram': 1.740,
        'disk': 160,
        'bandwidth': None
    },
    'm1.medium': {
        'id': 'm1.medium',
        'name': 'Medium Instance',
        'cpus': 1,
        'ram': 3.700,
        'disk': 410,
        'bandwidth': None
    },
    'm1.large': {
        'id': 'm1.large',
        'name': 'Large Instance',
        'cpus': 2,
        'ram': 7.680,
        'disk': 850,
        'bandwidth': None
    },
    'm1.xlarge': {
        'id': 'm1.xlarge',
        'name': 'Extra Large Instance',
        'cpus': 4,
        'ram': 15.360,
        'disk': 1690,
        'bandwidth': None
    },
    'c1.medium': {
        'id': 'c1.medium',
        'name': 'High-CPU Medium Instance',
        'cpus': 2,
        'ram': 1.740,
        'disk': 350,
        'bandwidth': None
    },
    'c1.xlarge': {
        'id': 'c1.xlarge',
        'name': 'High-CPU Extra Large Instance',
        'cpus': 8,
        'ram': 7.680,
        'disk': 1690,
        'bandwidth': None
    },
    'm2.xlarge': {
        'id': 'm2.xlarge',
        'name': 'High-Memory Extra Large Instance',
        'cpus': 2,
        'ram': 17.510,
        'disk': 420,
        'bandwidth': None
    },
    'm2.2xlarge': {
        'id': 'm2.2xlarge',
        'name': 'High-Memory Double Extra Large Instance',
        'cpus': 4,
        'ram': 35.021,
        'disk': 850,
        'bandwidth': None
    },
    'm2.4xlarge': {
        'id': 'm2.4xlarge',
        'name': 'High-Memory Quadruple Extra Large Instance',
        'cpus': 1,
        'ram': 70.042,
        'disk': 1690,
        'bandwidth': None
    },
    'm3.medium': {
        'id': 'm3.medium',
        'name': 'Medium Instance',
        'cpus': 1,
        'ram': 3.840,
        'disk': 4000,
        'bandwidth': None
    },
    'm3.large': {
        'id': 'm3.large',
        'name': 'Large Instance',
        'cpus': 2,
        'ram': 7.168,
        'disk': 32000,
        'bandwidth': None
    },
    'm3.xlarge': {
        'id': 'm3.xlarge',
        'name': 'Extra Large Instance',
        'cpus': 4,
        'ram': 15.360,
        'disk': 80000,
        'bandwidth': None
    },
    'm3.2xlarge': {
        'id': 'm3.2xlarge',
        'name': 'Double Extra Large Instance',
        'cpus': 8,
        'ram': 30.720,
        'disk': 160000,
        'bandwidth': None
    },
    'cg1.4xlarge': {
        'id': 'cg1.4xlarge',
        'name': 'Cluster GPU Quadruple Extra Large Instance',
        'cpus': 64,
        'ram': 22.528,
        'disk': 1690,
        'bandwidth': None
    },
    # c3 instances have 2 SSDs of the specified disk size
    'c3.large': {
        'id': 'c3.large',
        'name': 'Compute Optimized Large Instance',
        'cpus': 2,
        'ram': 3.750,
        'disk': 16,
        'bandwidth': None
    },
    'c3.xlarge': {
        'id': 'c3.xlarge',
        'name': 'Compute Optimized Extra Large Instance',
        'cpus': 4,
        'ram': 7.000,
        'disk': 40,
        'bandwidth': None
    },
    'c3.2xlarge': {
        'id': 'c3.2xlarge',
        'name': 'Compute Optimized Double Extra Large Instance',
        'cpus': 8,
        'ram': 15.000,
        'disk': 80,
        'bandwidth': None
    },
    'c3.4xlarge': {
        'id': 'c3.4xlarge',
        'name': 'Compute Optimized Quadruple Extra Large Instance',
        'cpus': 16,
        'ram': 30.000,
        'disk': 160,
        'bandwidth': None
    },
    'c3.8xlarge': {
        'id': 'c3.8xlarge',
        'name': 'Compute Optimized Eight Extra Large Instance',
        'cpus': 32,
        'ram': 60.000,
        'disk': 320,
        'bandwidth': None
    },
    'cr1.8xlarge': {
        'id': 'cr1.8xlarge',
        'name': 'High Memory Cluster Eight Extra Large',
        'cpus': 32,
        'ram': 24.4000,
        'disk': 240,
        'bandwidth': None
    },
    'hs1.8xlarge': {
        'id': 'hs1.8xlarge',
        'name': 'High Storage Eight Extra Large Instance',
        'cpus': 16,
        'ram': 11.9808,
        'disk': 48000,
        'bandwidth': None
    },
    # i2 instances have up to eight SSD drives
    'i2.xlarge': {
        'id': 'i2.xlarge',
        'name': 'High Storage Optimized Extra Large Instance',
        'cpus': 4,
        'ram': 31.232,
        'disk': 800,
        'bandwidth': None
    },
    'i2.2xlarge': {
        'id': 'i2.2xlarge',
        'name': 'High Storage Optimized Double Extra Large Instance',
        'cpus': 8,
        'ram': 62.464,
        'disk': 1600,
        'bandwidth': None
    },
    'i2.4xlarge': {
        'id': 'i2.4xlarge',
        'name': 'High Storage Optimized Quadruple Large Instance',
        'cpus': 16,
        'ram': 12.4928,
        'disk': 3200,
        'bandwidth': None
    },
    'i2.8xlarge': {
        'id': 'i2.8xlarge',
        'name': 'High Storage Optimized Eight Extra Large Instance',
        'cpus': 32,
        'ram': 24.9856,
        'disk': 6400,
        'bandwidth': None
    },
}
