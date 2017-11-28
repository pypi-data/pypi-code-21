#!/usr/bin/env python

import bob.paper.taslp_2017.database


avspoof_input_dir = "/idiap/project/lobi/AVSpoof/data/"
avspoof_input_ext = ".wav"


database = bob.paper.taslp_2017.database.AVspoofPadDatabase(
    protocol = 'logical_access',
    original_directory=avspoof_input_dir,
    original_extension=avspoof_input_ext,
    training_depends_on_protocol=True,
)
