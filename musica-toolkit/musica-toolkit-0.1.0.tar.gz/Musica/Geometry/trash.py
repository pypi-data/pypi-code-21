    ##############################################

    def _compose_transformation(self, transformation):

        return np.matmul(self._m, transformation.array)

    ##############################################

    def _transform_vector(self, vector):

        array = np.matmul(self._m, np.transpose(vector.v))
        return Vector2D(array)

    ##############################################

    def _transform_vectors(self, vectors):

        # Fixme: check Vector2D ???

        return [self._transform_vectors(vector) for vector in vectors]

    #######################################

    def __mul__(self, obj):

        if isinstance(obj, Transformation):
            array = self._compose_transformation(obj)
            return self.__class__(array)
        elif isinstance(obj, Vector2D):
            return self._transform_vector(obj)
        elif isinstance(obj, Primitive): # Fixme: try transform ?
            return obj.transform(self)
        elif isinstance(obj, (list, tuple)): # Fixme: iterable
            return self._transform_vectors(obj)
        else:
            raise ValueError

        # try:
        #     return self._transform_vectors(obj)
        # except TypeError:
        #     raise ValueError

    #######################################

    def __imul__(self, obj):

        if isinstance(obj, Transformation):
            self._m = self._compose_transformation(obj)
        else:
            raise ValueError

        return self
