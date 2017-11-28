import bob.bio.base

# define a queue with demanding parameters
grid = bob.bio.base.grid.Grid(
  number_of_scoring_jobs = 1,
  number_of_enrollment_jobs = 1,
  training_queue = '16G',
  # preprocessing
  preprocessing_queue = '2G',
  # feature extraction
  extraction_queue = '2G',
  # feature projection
  projection_queue = '2G',
  # model enrollment
  enrollment_queue = '4G-io-big',
  # scoring
  scoring_queue = '4G-io-big',
  number_of_preprocessing_jobs = 48,
  number_of_extraction_jobs = 48,
  number_of_projection_jobs = 64
)
