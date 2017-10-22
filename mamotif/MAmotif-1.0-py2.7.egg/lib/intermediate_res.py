# def save_classifier(classifier, file_name):
#         """
#         save classifier result into a file
#         @param file_name:
#         """
#         import cPickle
#         if not file_name.endswith('.classifier'):
#             cPickle.dump(classifier, file(file_name + '.classifier', 'wb'), True)
#         else:
#             cPickle.dump(classifier, file(file_name, 'wb'), True)
#
#
# def read_classifier(file_path):
#     """
#     read a classifier result from file
#     """
#     import cPickle
#     if file_path.endswith('.classifier'):
#         cls = cPickle.load(file(file_path, 'rb'))
#         return cls
#     else:
#         print 'This file is not a classifier file!'
#
#
# def save_PeakSet(pkset, file_name):
#     """
#     save peak set into a file
#     @param pkset: instance of GESet
#     @param file_name: file name for saving
#     """
#     import cPickle
#     if not file_name.endswith('.PeakSet'):
#         cPickle.dump(pkset, file(file_name + '.PeakSet', 'wb'), True)
#     else:
#         cPickle.dump(pkset, file(file_name, 'wb'), True)
#
#
# def read_PeakSet(file_path):
#     """
#     read PeakSet from file
#     """
#     import cPickle
#     if file_path.endswith('.PeakSet'):
#         pkset = cPickle.load(file(file_path, 'rb'))
#         return pkset
#     else:
#         print 'This file is not a PeakSet file!'
#
#
# def save_GESet(geset, file_name):
#     """
#     save gene expression set data into a file
#     @param geset: instance of GESet
#     @param file_name: file name for saving
#     """
#     import cPickle
#     if not file_name.endswith('.GESet'):
#         cPickle.dump(geset, file(file_name + '.GESet', 'wb'), True)
#     else:
#         cPickle.dump(geset, file(file_name, 'wb'), True)
#
#
# def read_GESet(file_path):
#     """
#     read GESet from file
#     """
#     import cPickle
#     if file_path.endswith('.GESet'):
#         geset = cPickle.load(file(file_path, 'rb'))
#         return geset
#     else:
#         print 'This file is not a GESet file!'
#
#
# def save_GeneSet(geneset, file_name):
#     """
#     saving gene set
#     @param file_path:
#     """
#     import cPickle
#     if not file_name.endswith('.GeneSet'):
#         cPickle.dump(geneset, file(file_name + '.GeneSet', 'wb'), True)
#     else:
#         cPickle.dump(geneset, file(file_name, 'wb'), True)
#
#
# def read_GeneSet(file_path):
#     """
#     read GeneSet from file
#     """
#     import cPickle
#     if file_path.endswith('.GeneSet'):
#         geneset = cPickle.load(file(file_path, 'rb'))
#         return geneset
#     else:
#         print 'This file is not a GeneSet file!'