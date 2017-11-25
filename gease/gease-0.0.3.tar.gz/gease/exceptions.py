class ReleaseExistException(Exception):
    pass


class RepoNotFoundError(Exception):
    pass


class GitHubException(Exception):
    pass


class NoGeaseConfigFound(Exception):
    pass


class AbnormalGithubResponse(Exception):
    pass


class UnhandledException(Exception):
    pass
