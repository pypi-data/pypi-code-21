#!/usr/local/bin/python3
import requests

def get_digest(registry, repository, tag):
    manifest_url = f"https://{registry}/v2/{repository}/manifests/{tag}"
    headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
    r = requests.head(manifest_url, headers=headers)
    if r.status_code == 401:
        token_url = f"https://auth.docker.io/token"
        token_params = {
            "service": "registry.docker.io",
            "scope": f"repository:{repository}:pull"
        }
        token = requests.get(token_url, params=token_params, json=True).json()["token"]
        headers["Authorization"] = f"Bearer {token}"
        r = requests.head(manifest_url, headers=headers)
    return r.headers['Docker-Content-Digest']

def get_parts(reference):
    # Docker default values
    registry = "registry-1.docker.io"
    repository = reference
    tag = "latest"
    digest = None
    # Parse domain part, if any
    if "/" in reference:
        domain, remainder = reference.split("/", 1)
        if domain == "localhost" or "." in domain:
            registry = domain
            repository = remainder
    # Separate image reference and digest
    if "@" in repository:
        repository, digest = repository.split("@", 1)
    # See if image contains a tag
    if ":" in repository:
        repository, tag = repository.split(":", 1)
    # Handle "familiar" Docker references
    if registry == "registry-1.docker.io" and "/" not in repository:
        repository = "library/" + repository
    if not digest:
        digest = get_digest(registry, repository, tag)
    return (registry, repository, tag, digest)

def get_reference(registry, repository, digest):
    return f"{registry}/{repository}@{digest}"