"""
Batching support.

"""


def batched(resources, batch_size, **kwargs):
    """
    Chunk resources into batches with a common type.

    """
    previous = 0
    for index, resource in enumerate(resources):
        different_type = resource.type != resources[previous].type
        too_many = index - previous >= batch_size

        if different_type or too_many:
            yield resources[previous:index]
            previous = index

    yield resources[previous:]
