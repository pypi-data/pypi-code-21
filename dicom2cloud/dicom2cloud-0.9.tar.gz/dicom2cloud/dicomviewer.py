import dicom
import pylab

def main():
    filename ='D:\\Projects\\clinic2cloud\\exampleData\\7T_mp2rage_Atlasing_sorted\\GR_IR_M_10_mp2rage-wip900_0.75iso_7T_UNI-DEN\\00140_tfl3d1_ns_C_A32.IMA'
    ds = dicom.read_file(filename)
    pylab.imshow(ds.pixel_array, cmap=pylab.cm.bone)
    pylab.show()

if __name__ == '__main__':
    main()