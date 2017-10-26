import os
from astropy.io import fits
import a99


__all__ = ["overwrite_fits"]


def overwrite_fits(hdulist, filename):
    """
    Saves a FITS file. Combined file rename, save new, delete renamed for FITS files
    Why: HDUlist.writeto() does not overwrite existing files
    Why(2): It is also a standardized way to save FITS files
    """

    assert isinstance(hdulist, (fits.HDUList, fits.PrimaryHDU))
    temp_name = None
    flag_delete_temp = False
    if os.path.isfile(filename):
        # PyFITS does not overwrite file
        temp_name = a99.rename_to_temp(filename)
    try:
        hdulist.writeto(filename, output_verify='warn')
        flag_delete_temp = temp_name is not None
    except:
        # Writing failed, reverts renaming
        os.rename(temp_name, filename)
        raise

    if flag_delete_temp:
        os.unlink(temp_name)


