depends = ('ITKPyBase', 'ITKSmoothing', 'ITKImageStatistics', 'ITKImageIntensity', 'ITKImageFilterBase', 'ITKImageFeature', 'ITKCommon', )
templates = (
  ('KrcahSheetnessFeatureImageFilter', 'itk::KrcahSheetnessFeatureImageFilter', 'itkKrcahSheetnessFeatureImageFilterISS2IF2', True, 'itk::Image< signed short,2 >, itk::Image< float,2 >'),
  ('KrcahSheetnessFeatureImageFilter', 'itk::KrcahSheetnessFeatureImageFilter', 'itkKrcahSheetnessFeatureImageFilterISS3IF3', True, 'itk::Image< signed short,3 >, itk::Image< float,3 >'),
  ('KrcahSheetnessFeatureImageFilter', 'itk::KrcahSheetnessFeatureImageFilter', 'itkKrcahSheetnessFeatureImageFilterIUC2IF2', True, 'itk::Image< unsigned char,2 >, itk::Image< float,2 >'),
  ('KrcahSheetnessFeatureImageFilter', 'itk::KrcahSheetnessFeatureImageFilter', 'itkKrcahSheetnessFeatureImageFilterIUC3IF3', True, 'itk::Image< unsigned char,3 >, itk::Image< float,3 >'),
  ('KrcahSheetnessFeatureImageFilter', 'itk::KrcahSheetnessFeatureImageFilter', 'itkKrcahSheetnessFeatureImageFilterIF2IF2', True, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('KrcahSheetnessFeatureImageFilter', 'itk::KrcahSheetnessFeatureImageFilter', 'itkKrcahSheetnessFeatureImageFilterIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
)
