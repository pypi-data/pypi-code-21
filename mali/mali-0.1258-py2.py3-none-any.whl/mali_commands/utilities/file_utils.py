def get_content_type(body):
    import puremagic
    import mimetypes
    mimetypes.init()
    mimetypes.add_type(mimetypes.types_map.get('.jpg'), '.jfif')

    try:
        ext = puremagic.from_string(body)
        return mimetypes.types_map.get(ext)
    except puremagic.PureError:
        return None
