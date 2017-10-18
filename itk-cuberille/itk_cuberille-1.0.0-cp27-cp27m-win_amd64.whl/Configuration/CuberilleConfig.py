depends = ('ITKPyBase', 'ITKMesh', 'ITKImageGradient', 'ITKImageFunction', 'ITKCommon', )
templates = (
  ('CuberilleImageToMeshFilter', 'itk::CuberilleImageToMeshFilter', 'itkCuberilleImageToMeshFilterIF2MF2DSMF22FF', True, 'itk::Image< float,2 >, itk::Mesh< float,2,itk::DefaultStaticMeshTraits<float,2,2,float,float > >'),
  ('CuberilleImageToMeshFilter', 'itk::CuberilleImageToMeshFilter', 'itkCuberilleImageToMeshFilterID2MD2DSMD22DD', True, 'itk::Image< double,2 >, itk::Mesh< double,2,itk::DefaultStaticMeshTraits<double,2,2,double,double > >'),
  ('CuberilleImageToMeshFilter', 'itk::CuberilleImageToMeshFilter', 'itkCuberilleImageToMeshFilterIF3MF3DSMF33FF', True, 'itk::Image< float,3 >, itk::Mesh< float,3,itk::DefaultStaticMeshTraits<float,3,3,float,float > >'),
  ('CuberilleImageToMeshFilter', 'itk::CuberilleImageToMeshFilter', 'itkCuberilleImageToMeshFilterID3MD3DSMD33DD', True, 'itk::Image< double,3 >, itk::Mesh< double,3,itk::DefaultStaticMeshTraits<double,3,3,double,double > >'),
)
