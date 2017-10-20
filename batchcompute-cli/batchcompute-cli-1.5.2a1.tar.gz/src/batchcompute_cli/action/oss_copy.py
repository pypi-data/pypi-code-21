from ..util import oss_client
from terminal import green,gray
import sys



def copy(source, target):

    (bucket, key, region) = oss_client.parse_oss_path(source)
    bucket_tool = oss_client.get_bucket_tool(bucket,region)

    (target_bucket, target_key, target_region) = oss_client.parse_oss_path(target)
    target_bucket_tool = oss_client.get_bucket_tool(target_bucket, target_region)


    ### print
    print(gray('copy from %s to %s' % (source,target)))


    if key.endswith('/'):
        # folder -> folder
        target_key = target_key if target_key.endswith('/') else target_key+'/'

        if bucket == target_bucket:
            # in same bucket

            flag = True
            while(flag):
                obj = bucket_tool.list_objects(key)
                source_arr = obj.object_list
                for k in source_arr:
                    name = k.key[k.key.rfind('/')+1:]
                    target_name = target_key+name
                    bucket_tool.copy_object(bucket, k.key, target_name)
                    print('%s done' % target_name)
                if not obj.next_marker:
                    flag = False
        else:
            # diff bucket
            flag = True
            while (flag):
                obj = bucket_tool.list_objects(key)
                source_arr = obj.object_list
                for k in source_arr:
                    name = k.key[k.key.rfind('/') + 1:]
                    target_name = target_key + name
                    target_bucket_tool.put_object(target_name, bucket_tool.get_object(k.key), progress_callback=progFn)

                    print('%s done' % target_name)
                if not obj.next_marker:
                    flag = False

    else:
        target_name = target_key
        if target_key.endswith('/'):
            name = key[key.rfind('/')+1:]
            target_name= target_key+ name


        if bucket == target_bucket:
            bucket_tool.copy_object(bucket, key, target_name)
        else:
            target_bucket_tool.put_object(target_name, bucket_tool.get_object(key), progress_callback=progFn)

        print('%s done\n' % target)
    print(green('done'))


def progFn(a,b):
    if not a or not b:
        return

    if a != b:
        p = int(a * 50 / b)
        s = ('%s %s%%\r' % ('#' * p, p * 2))
    else:
        s = ('%s 100%%\n' % ('#' * 50))
    sys.stdout.write(s)
    sys.stdout.flush()