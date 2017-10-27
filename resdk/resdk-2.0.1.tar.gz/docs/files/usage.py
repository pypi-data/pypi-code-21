import resdk

# Create a Resolwe object to interact with the server
res = resdk.Resolwe(url='https://app.genialis.com')

# Enable verbose logging to standard output
resdk.start_logging()

# Get sample meta-data from the server
sample = res.sample.get('mouse-example-chr19')

# Download files associated with the sample
sample.download()
