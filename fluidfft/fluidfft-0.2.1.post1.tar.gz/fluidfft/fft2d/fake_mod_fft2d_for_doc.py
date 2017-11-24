
class FFT2dFakeForDoc(object):
    """Class to perform Fast Fourier Transform in 2d."""
    def __init__(self, n0=2, n1=2):
        pass

    def get_short_name(self):
        pass

    def get_local_size_X(self):
        pass

    def run_tests(self):
        """Run the c++ tests."""

    def run_benchs(self, nb_time_execute=10):
        """Run the c++ benchmarcks"""

    def fft_as_arg(self, fieldX, fieldK):
        """Perform the fft and copy the result in the second argument."""

    def ifft_as_arg(self, fieldK, fieldX):
        """Perform the ifft and copy the result in the second argument."""

    def fft(self, fieldX):
        """Perform the fft and returns the result."""

    def ifft(self, fieldK):
        """Perform the ifft and returns the result."""

    def get_shapeX_loc(self):
        """Get the local shape of the array in the "real space"."""

    def get_shapeK_loc(self):
        """Get the local shape of the array in the Fourier space"""

    def get_shapeX_seq(self):
        """Get the shape of the real array as it would be with nb_proc = 1"""

    def get_shapeK_seq(self):
        """Get the shape of the complex array as it would be with nb_proc = 1

        Warning: if get_is_transposed(), the complex array would also be
        transposed, so in this case, one should write:: 

          nKy = self.get_shapeK_seq[1]

        """

    def get_is_transposed(self):
        """Get the boolean "is_transposed"."""

    def get_seq_indices_first_X(self):
        pass

    def get_seq_indices_first_K(self):
        pass

    def get_k_adim_loc(self):
        pass

    def get_x_adim_loc(self):
        pass

    def compute_energy_from_X(self, fieldX):
        pass

    def compute_energy_from_K(self, fieldK):
        pass

    def sum_wavenumbers(self, fieldK):
        pass

    def gather_Xspace(self, ff_loc, root=None):
        """Gather an array in real space for a parallel run."""

    def scatter_Xspace(self, ff_seq, root=None):
        """Scatter an array in real space for a parallel run."""
