depends = ('ITKPyBase', 'ITKTransform', )
templates = (
  ('CartesianToPolarTransform', 'itk::CartesianToPolarTransform', 'itkCartesianToPolarTransformD2', True, 'double,2'),
  ('CartesianToPolarTransform', 'itk::CartesianToPolarTransform', 'itkCartesianToPolarTransformD3', True, 'double,3'),
  ('PolarToCartesianTransform', 'itk::PolarToCartesianTransform', 'itkPolarToCartesianTransformD2', True, 'double,2'),
  ('PolarToCartesianTransform', 'itk::PolarToCartesianTransform', 'itkPolarToCartesianTransformD3', True, 'double,3'),
)
