import os
from pathlib import Path
from .json_utils import json_hash

class MetadataGenerator(object):
    """
    A metadata generator automatically launches a specified Docker container on
    matching IPTK datasets. The spawned containers will have the dataset's data
    mounted on /input and are expected to write their generated metadata to
    /output. Execution time for the container may be limited on some systems.
    Metadata should pereferably written to .json files to facilitate indexing.
    The optional conditions array may specify a range of Unix shell patterns, 
    the Docker container will only be created if all of them match at least one
    file. Patterns are evaluated relative to the data/ directory. Non-relative
    patterns are unsupported.
    """
    def __init__(self, registry, repository, digest, conditions=[]):
        super(MetadataGenerator, self).__init__()
        self.registry = registry
        self.repository = repository
        self.digest = digest
        self.conditions = conditions

    def spec(self):
        spec = {
            "registry": self.registry,
            "repository": self.repository,
            "digest": self.digest,
            "conditions": self.conditions
        }
        return spec
    
    def should_fire(self, dataset):
        for condition in self.conditions:
            generator = Path(dataset.data_path).glob(condition)
            if not next(generator, None):
                return False
        return True
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.repository}>"
        
class MetadataSpec(object):
    """
    IPTK supports the storage of arbitrary metadata within a dataset's meta/
    directory. The MetadataSpec class provides uniquie identifiers for each
    metadata collection. Identifiers are generated from the organization, name,
    and version fields of a MetadataSpec.
    """
    def __init__(self, organization: str, name: str, version: int, generator: MetadataGenerator=None):
        super(MetadataSpec, self).__init__()
        self.organization = organization
        self.name = name
        self.version = version
        self.generator = generator
    
    @property
    def spec(self):
        spec = {
            "name": self.name,
            "organization": self.organization,
            "version": self.version,
            "generator": self.generator.spec()
        }
        return spec
        
    @property
    def identifier(self):
        return json_hash(self.spec)
        
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.identifier}>"