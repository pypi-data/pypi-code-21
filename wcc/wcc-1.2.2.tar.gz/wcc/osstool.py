# -*- coding: utf-8 -*-
import os
import shutil
import oss2


# 以下代码展示了基本的文件上传、下载、罗列、删除用法。


# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
#
# 以杭州区域为例，Endpoint可以是：
#   http://oss-cn-hangzhou.aliyuncs.com
#   https://oss-cn-hangzhou.aliyuncs.com
# 分别以HTTP、HTTPS协议访问。
access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'LTAIu27qRBMqFN5N')
access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', '2Oyom9GlxfDF5vg3BUYyVG45lZLiEr')
bucket_name = os.getenv('OSS_TEST_BUCKET', 'wikicivi-files')
endpoint = os.getenv('OSS_TEST_ENDPOINT', 'http://oss-cn-qingdao.aliyuncs.com')


# 确认上面的参数都填写正确了
for param in (access_key_id, access_key_secret, bucket_name, endpoint):
    assert '<' not in param, '请设置参数：' + param

# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)


#bucket.put_object_from_file('云上座右铭.txt', '本地座右铭.txt')
file_object = open('./delete_files.txt') 
try: 
	for line in file_object: 
		print(line)
		continue
		# 删除名为motto.txt的Object
		bucket.delete_object(line)
		# 确认Object已经被删除了
		assert not bucket.object_exists('motto.txt')
		# 获取不存在的文件会抛出oss2.exceptions.NoSuchKey异常
		try:
			bucket.get_object('云上座右铭.txt')
		except oss2.exceptions.NoSuchKey as e:
			print(u'已经被删除了：request_id={0}'.format(e.request_id))
		else:
			assert False
finally: 
	file_object.close() 



# 也可以批量删除
# 注意：重复删除motto.txt，并不会报错
#bucket.batch_delete_objects(['motto.txt', '云上座右铭.txt'])



# 清除本地文件
os.remove(u'本地文件名.txt')
os.remove(u'本地座右铭.txt')
