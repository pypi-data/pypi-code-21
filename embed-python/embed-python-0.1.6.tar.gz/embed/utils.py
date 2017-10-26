def to_chunks(items, chunks_of=4):
    return [
        items[i:i + chunks_of] for i in range(0, len(items), chunks_of)
    ]

