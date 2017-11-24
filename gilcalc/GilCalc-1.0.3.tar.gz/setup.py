
from distutils.core import setup #如果没有需要先安装
setup(name='GilCalc',  #打包后的包文件名 
      version='1.0.3',   #版本
      description='聚源计算python接口',   
      author='wanjian',   
      author_email='wanjian@gildata.com',   
      url=' ',   
      py_modules=['GilCalc'],   #与前面的新建文件名一致 
      install_requires=["requests"]
) 
