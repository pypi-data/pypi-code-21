from ..util import config,oss_client
from terminal import green,blue

def pwd():
    osspath = config.get_oss_path()
    print('%s : %s' % (blue('osspath'), green(osspath)))

    (bucket, key, region) = oss_client.parse_oss_path(osspath)

    print('%s : %s' % (blue('bucket'), bucket))
    print('%s : %s' % (blue('key'), key))

