import azure_face_api as afa

face = afa.face()
face.set_key('KEY')
print(face.make_request('https://c2.staticflickr.com/2/1388/1082003977_664e76425b_z.jpg'))
print(face.make_request('C:\\test.jpg'))
