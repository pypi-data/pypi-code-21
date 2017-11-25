import prmt

def should_run_any(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='Run ANY PUBLISH COMMANDS?\n',
        default=default,
        margin=margin,
    )


def should_update_version(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='BUMP VERSION number?\n',
        default=default,
        margin=margin,
    )


def should_run_build_file(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='Do you want to RUN BUILD FILE before publishing?\n',
        default=default,
        margin=margin
    )

def should_build_wheel(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='Do you want to BUILD new WHEEL?\n',
        default=default,
        margin=margin
    )


def should_push_gemfury(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='Do you want to PUSH the new version to GEMFURY?\n',
        default=default,
        margin=margin
    )


def should_push_pypi(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='Do you want to PUSH the new version to PYPI?\n',
        default=default,
        margin=margin
    )

