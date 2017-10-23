from fdfs_client.client import *


class FastDfsManager(object):
    def __init__(self,clientFile=''):
        self.__domainName = 'http://www.igap.cc/'
        if clientFile == '':
            self.__client_file = os.getcwd() + '/Conf/fastDfsClient.conf'
        else:
            self.__client_file = clientFile

    def upload_to_fastdfs(self, source_file):
        try:
            client = Fdfs_client(self.__client_file)
            ret_upload = client.upload_by_filename(source_file)
        except Exception as e:
            return None
        if ret_upload.get('Status','') == 'Upload successed.':
            return self.__domainName + ret_upload['Remote file_id']
        else:
            return None

    def download_fastdfs_file(self, source_file, dest_file_name):
        client = Fdfs_client(self.__client_file)
        j = len(self.__domainName)
        s = source_file[:j].lower()
        if s == self.__domainName.lower():
            sFile = source_file[j:]
        else:
            sFile = source_file
        ret_download = client.download_to_file(dest_file_name, sFile)
        if ret_download.get('Download size',''):
            return dest_file_name
        else:
            return None

if __name__ == '__main__':
    fileManager = FastDfsManager('/root/work/testing-platform-execute/Conf/fastDfsClient.conf')
    # result = fileManager.uploadToFastDFS('/data/02.jmx')
    # print(result)
    #
    # fileName = fileManager.directoryToZip('/data/02.zip',['/data/02.jmx'])
    # print(fileName)
    # result = fileManager.uploadToFastDFS('/data/001.zip')
    # print(result)
#     #
#     # result = fileManager.downloadFile(result,'/data/4.txt')
#     # print(result)
#     files = ['/data/01.txt','/data/02.jpg','/data/03.jpg','/data/04.jpg']
#     fileName = fileManager.directoryToZip('/data/1.zip',files)
#     print(fileName)
#     fileList = fileManager.zipToDirectory('/data/1.zip','/data/1')
#     print(fileList)
