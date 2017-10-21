# -*- coding: utf-8 -*-
"""
Raster tools for remote sensing data analysis

@author: Alan Xu
"""

import os
import subprocess
import numpy as np
import pandas as pd
import csv
from osgeo import gdal
from xml.etree import ElementTree as ET
from lxml import etree
from copy import deepcopy


def raster_clip(mask_file, in_file, out_file, resampling_method='near', out_format='Float32',
                srcnodata='nan', dstnodata='nan', max_memory='2000'):
    """
    for every input in_file, get the same spatial resolution, projection, and
    extent as the input mask_file.

    output is a new raster file: out_file.
    """

    # path2, ext2 = os.path.splitext(fileMask)
    # shpMask = '{}.shp'.format(path2)
    # subprocess.call(['gdaltindex', shpMask, fileMask], shell=True)

    in0 = gdal.Open(mask_file)
    prj0 = in0.GetProjection()
    extent0, res0 = get_raster_extent(in0)
    extent0 = ' '.join(map(str, extent0))
    res0 = ' '.join(map(str, res0))
    size0 = '{} {}'.format(str(in0.RasterXSize), str(in0.RasterYSize))

    in1 = gdal.Open(in_file)
    prj1 = in1.GetProjection()
    extent1, res1 = get_raster_extent(in1)
    extent1 = ' '.join(map(str, extent1))
    res1 = ' '.join(map(str, res1))

    # gdal_expression = (
    #     'gdalwarp -s_srs {} -t_srs {} -te {} -ts {} '
    #     '-srcnodata {} -dstnodata {} -wm {} -multi -overwrite '
    #     '-co COMPRESS=DEFLATE -co ZLEVEL=9 -co PREDICTOR=2 -co BIGTIFF=YES '
    #     '-r {} -ot {} "{}" "{}"').format(
    #     prj1, prj0, extent0, size0, srcnodata, dstnodata, max_memory,
    #     resampling_method, out_format, in_file, out_file)
    gdal_expression = (
        'gdalwarp -t_srs {} -te {} -ts {} '
        '-srcnodata {} -dstnodata {} -multi -overwrite '
        '-co COMPRESS=LZW -co PREDICTOR=2 -co BIGTIFF=YES '
        '-r {} -ot {} "{}" "{}"').format(
        prj0, extent0, size0, srcnodata, dstnodata,
        resampling_method, out_format, in_file, out_file)
    # gdal_expression = (
    #     'gdalwarp -s_srs {} -t_srs {} -te {} -ts {} '
    #     '-srcnodata {} -dstnodata {} -wm {} -multi -overwrite '
    #     '-co COMPRESS=LZW -co PREDICTOR=2 -co BIGTIFF=YES '
    #     '-r {} -ot {} "{}" "{}"').format(
    #     prj1, prj0, extent0, size0, srcnodata, dstnodata, max_memory,
    #     resampling_method, out_format, in_file, out_file)
    print(gdal_expression)
    subprocess.check_output(gdal_expression, shell=True)

    # if (prj0 != prj1) or (extent0 != extent1) or (res0 != res1):
    #     gdal_expression = (
    #         'gdalwarp -s_srs {} -t_srs {} -te {} -ts {} '
    #         '-srcnodata {} -dstnodata {} -wm {} -multi -overwrite '
    #         '-co COMPRESS=LZW -co PREDICTOR=2 -co TILED=YES -co BIGTIFF=YES '
    #         '-r {} "{}" "{}"').format(
    #         prj1, prj0, extent0, size0, srcnodata, dstnodata, max_memory,
    #         resampling_method, in_file, out_file)
    #     subprocess.check_output(gdal_expression, shell=True)
    # else:
    #     shutil.copy(in_file, out_file)

    in0 = None
    in1 = None

    return


def raster_clip_batch1(input_mask, in_file_list, input_x, resampling_method='average', no_data='-999'):
    """
    batch processing of multiple input tif files
    :param input_mask:
    :param in_file_list:
    :param input_x:
    :return:
    """
    with open(in_file_list, "w") as txt0:
        print(input_mask, file=txt0)
        for i, file_name in enumerate(input_x):
            print(i, file_name)
            output_x = '{}_reg.tif'.format(os.path.splitext(file_name)[0])
            raster_clip(input_mask, file_name, output_x, resampling_method, srcnodata=no_data, dstnodata='nan')
            print(output_x, file=txt0)
    return


def ogrvrt_to_grid(mask_file, csv_file, x_column, y_column, z_column, out_file, dst_nodata='nan', a_interp='nearest'):
    """
    Convert xyz file with geolocation information back to the geotiff raster format.
    :param mask_file: reference raster file
    :param csv_file: csv file with actual values (x,y,z)
    :param x_column: column name for x
    :param y_column: column name for y
    :param z_column: column name for z
    :param out_file: output file (no extension)
    :param dst_nodata: no data value
    :return:
    """
    out_file_vrt = '{}.vrt'.format(out_file)
    root = ET.Element('OGRVRTDataSource')
    tree = ET.ElementTree(root)
    OGRVRTLayer = ET.SubElement(root, 'OGRVRTLayer', name=os.path.splitext(os.path.basename(csv_file))[0])
    SrcDataSource = ET.SubElement(OGRVRTLayer, 'SrcDataSource')
    SrcDataSource.text = csv_file
    GeometryType = ET.SubElement(OGRVRTLayer, 'GeometryType')
    GeometryType.text = 'wkbPoint'
    ET.SubElement(OGRVRTLayer, 'GeometryField', encoding="PointFromColumns", x=x_column, y=y_column, z=z_column)
    with open(out_file_vrt, 'wb') as vrt0:
        tree.write(vrt0)

    out_file_tif = '{}.tif'.format(out_file)
    in0 = gdal.Open(mask_file)
    prj0 = in0.GetProjection()
    extent0, res0 = get_raster_extent(in0)
    extent0 = ' '.join(map(str, extent0))
    ext_x = '{} {}'.format(str(extent0[0]), str(extent0[2]))
    ext_y = '{} {}'.format(str(extent0[3]), str(extent0[1]))
    size0 = '{} {}'.format(str(in0.RasterXSize), str(in0.RasterYSize))
    in0 = None
    in_layer = os.path.splitext(os.path.basename(csv_file))[0]
    # gdal_expression_01 = (
    #     'gdal_grid -ot Float32 -txe {} -tye {} -outsize {} -a_srs {} '
    #     '-co COMPRESS=LZW -co PREDICTOR=2 -co BIGTIFF=YES '
    #     '-a {}:radius1={}:radius2={}:nodata={} -l {} '
    #     '"{}" "{}" --config GDAL_NUM_THREADS ALL_CPUS --config GDAL_CACHEMAX 2000'
    # ).format(ext_x, ext_y, size0, prj0, a_interp, res0[0]*0.56, res0[1]*0.56, dst_nodata, in_layer, out_file_vrt, out_file_tif)
    gdal_expression_01 = (
        'gdal_rasterize -ot Float32 -a_srs {} -te {} -ts {} -a_nodata {} -init {} '
        '-co COMPRESS=LZW -co PREDICTOR=2 -co BIGTIFF=YES '
        '-3d -l {} "{}" "{}" --config GDAL_NUM_THREADS ALL_CPUS'
        # '-burn 0 -3d -l {} "{}" "{}" --config GDAL_NUM_THREADS ALL_CPUS'
    ).format(prj0, extent0, size0, dst_nodata, dst_nodata, in_layer, out_file_vrt, out_file_tif)
    # print(gdal_expression_01)
    subprocess.check_output(gdal_expression_01, shell=True)
    return


def csv_to_ogrvrt(csv_file, x_column, y_column, z_column, out_file):
    """
    Convert csv files with the same observations (rows) to gdal ogr vrt format.
    :param csv_file: csv file with actual values (x,y,z)
    :param x_column: column name for x
    :param y_column: column name for y
    :param z_column: column name for z
    :param out_file: output file name
    :return:
    """

    root = ET.Element('OGRVRTDataSource')
    tree = ET.ElementTree(root)
    OGRVRTLayer = ET.SubElement(root, 'OGRVRTLayer', name=os.path.splitext(os.path.basename(csv_file))[0])
    SrcDataSource = ET.SubElement(OGRVRTLayer, 'SrcDataSource')
    SrcDataSource.text = csv_file
    GeometryType = ET.SubElement(OGRVRTLayer, 'GeometryType')
    GeometryType.text = 'wkbPoint'
    ET.SubElement(OGRVRTLayer, 'GeometryField', encoding="PointFromColumns", x=x_column, y=y_column, z=z_column)

    with open(out_file, 'wb') as vrt0:
        tree.write(vrt0)

    return


def csv_to_libsvm(y_file, y_column, out_file, mask_column=-999):
    """
    Convert csv files with the same observations (rows) to gdal ogr vrt format.
    :param out_file: output file name
    :param y_file: csv file with actual values (x and y)
    :param y_column: column index for response variable y
    :param mask_column: column index for mask (if exist, and should be after popping y_column)
    :return:
    """
    i0 = open(y_file, newline='')
    o0 = open(out_file, 'w', newline='')
    reader0 = csv.reader(i0)
    writer0 = csv.writer(o0, delimiter=' ')
    n = 0
    for line0 in reader0:
        y_value = line0.pop(y_column)
        if mask_column > -999:
            del line0[mask_column]
        new_line = ['{}'.format(y_value)]
        for i, x_value in enumerate(line0):
            new_line.append('{}:{}'.format(i + 1, x_value))
        writer0.writerow(new_line)
        n += 1
        if n % 10000 == 0:
            print(n)
    i0.close()
    o0.close()

    return


def modify_vrt_xml(out_file_vrt):
    """
    modify the virtual raster format file to include multiple bands from each raster
    :param out_file_vrt:
    :return: field_names
    """
    vrt_doc = etree.parse(out_file_vrt)
    root = vrt_doc.getroot()
    path = os.path.dirname(out_file_vrt)
    n = 0
    field_names = []
    for element in root.iter('VRTRasterBand'):
        path_relative = element.xpath('.//SourceFilename/@relativeToVRT')
        file_text = element.xpath('.//SourceFilename/text()')
        if path_relative[0] == '0':
            file_name = file_text[0]
        else:
            file_name = os.path.join(path, file_text[0])
        in0 = gdal.Open(file_name)
        if in0.RasterCount == 1:
            n += 1
            element.attrib['band'] = str(n)
            field_names.append('{}_b1'.format(os.path.splitext(os.path.basename(file_text[0]))[0]))
        else:
            for band_num in range(in0.RasterCount):
                band_num += 1
                n += 1
                if band_num == 1:
                    element.attrib['band'] = str(n)
                    field_names.append('{}_b1'.format(os.path.splitext(os.path.basename(file_text[0]))[0]))
                else:
                    new_element = deepcopy(element)
                    new_element.attrib['band'] = str(n)
                    source_band = new_element.xpath('.//SourceBand')
                    source_band[0].text = str(band_num)
                    root.insert(root.index(element) + band_num - 1, new_element)
                    field_names.append('{}_b{}'.format(os.path.splitext(os.path.basename(file_text[0]))[0], band_num))
        in0 = None
    etree.ElementTree(root).write(out_file_vrt, pretty_print=True)
    return field_names


def build_stack_vrt(in_file_list, out_file):
    """
    build raster stack vrt file from in_file_list.
    :param in_file_list:
    :param out_file: output vrt file (end with .vrt)
    :return:
    """
    gdal_expression_01 = (
        'gdalbuildvrt -separate -overwrite -input_file_list "{}" "{}" --config GDAL_CACHEMAX 2000'
    ).format(in_file_list, out_file)
    # print(gdal_expression_01)
    subprocess.check_output(gdal_expression_01, shell=True)
    field_names = modify_vrt_xml(out_file)
    print(field_names)

    return field_names


def raster_to_h5(in_file_vrt, out_file_h5, field_names, mask_column, mask_valid_range=0, lines=100):
    """
    Make a layer stack of raster bands to be used in csv output.
    Output is a virtual raster with all bands and csv files with geolocation and valid data.
    All layers should be processed to have the same geolocation and dimensions.
    Mask band should be the 1st band in the in_file_list
    :param in_file_vrt: file name of the input virtual raster files
    :param out_file_h5: file name of output h5 file
    :param field_names: names of all columns
    :param mask_column: column used to mask data
    :param mask_valid_range: define valid data range (e.g.: >0)  in mask band
    :param lines: numbers of lines to read at once
    :return: None
    """

    in0 = gdal.Open(in_file_vrt)
    # print('Total number of raster bands: ', in0.RasterCount)
    bands = []
    for band_num in range(in0.RasterCount):
        band_num += 1
        band = in0.GetRasterBand(band_num)
        bands.append(band)
    dim0 = (0, 0, in0.RasterXSize, in0.RasterYSize)
    gt = in0.GetGeoTransform()

    with pd.HDFStore(out_file_h5, mode='w') as store:
        for y in range(dim0[1], dim0[3], lines):
            y2 = min(y + lines, dim0[3])
            lines1 = y2 - y
            cols, rows = np.meshgrid(np.arange(dim0[2]), np.arange(y, y2))
            geo_x = gt[0] + (cols + 0.5) * gt[1] + (rows + 0.5) * gt[2]
            geo_y = gt[3] + (cols + 0.5) * gt[4] + (rows + 0.5) * gt[5]
            data = np.vstack((geo_x.flatten(), geo_y.flatten()))
            for band in bands:
                band_data = band.ReadAsArray(dim0[0], y, dim0[2] - dim0[0], lines1).flatten()
                data = np.vstack((data, band_data))
            # df1 = pd.DataFrame(data, dtype='float32').transpose().dropna()
            df1 = pd.DataFrame(data, dtype='float32').transpose()
            df1.columns = ['x', 'y'] + field_names
            df0 = df1.loc[lambda df: df[mask_column] > mask_valid_range, :]
            store.append('df0', df0, index=False, data_columns=df0.columns)
    with pd.HDFStore(out_file_h5) as store:
        store.create_table_index('df0', columns=['x', 'y', mask_column], optlevel=6, kind='medium')
    in0 = None
    return


def raster_to_tiles(in_file_vrt, out_file_path, tile_x=1000, tile_y=1000, buffer_size=12, data_type='float32', no_data_value=None):
    """
    Build tiled rasters. Produce tiles when having at least 1 valid pixel
    :param in_file_vrt: file name of the input virtual/actual raster files
    :param out_file_path: output path for tiles
    :param tile_x: width of each tile
    :param tile_y: height of each tile
    :param buffer_size: buffer_size of each tile (pixels added to top, bottom, left and right)
    :param data_type: data type: float32 -> gdal.GDT_Float32, uint8 -> gdal.GDT_Byte
    :param no_data_value: No-Data value
    :return: None
    """

    in0 = gdal.Open(in_file_vrt)
    gt = in0.GetGeoTransform()
    proj = in0.GetProjection()
    print('Total number of raster bands: ', in0.RasterCount)
    bands = []
    for band_num in range(in0.RasterCount):
        band_num += 1
        band = in0.GetRasterBand(band_num)
        bands.append(band)

    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    for i in range(0, in0.RasterXSize, tile_x):
        for j in range(0, in0.RasterYSize, tile_y):
            if no_data_value is None:
                no_data_value = bands[0].GetNoDataValue()
            band_data = np.full((tile_y + buffer_size * 2, tile_x + buffer_size * 2), no_data_value, dtype=data_type)
            xmin = max(0, i - buffer_size)
            xs = xmin - i + buffer_size
            xmax = min(in0.RasterXSize - xmin, tile_x + buffer_size * 2 - xs)
            ymin = max(0, j - buffer_size)
            ys = ymin - j + buffer_size
            ymax = min(in0.RasterYSize - ymin, tile_y + buffer_size * 2 - ys)
            band_data[ys:ys+ymax, xs:xs+xmax] = bands[0].ReadAsArray(xmin, ymin, xmax, ymax)
            if no_data_value == band_data.min() == band_data.max():
                continue
            x2 = gt[0] + (i-buffer_size) * gt[1] + (j-buffer_size) * gt[2]
            y2 = gt[3] + (i-buffer_size) * gt[4] + (j-buffer_size) * gt[5]
            trans2 = (x2, gt[1], gt[2], y2, gt[4], gt[5])
            x_size = tile_x+buffer_size*2
            y_size = tile_y+buffer_size*2
            output_file = '{}_tile_{:06d}_{:06d}.tif'.format(os.path.splitext(os.path.basename(in_file_vrt))[0], i, j)
            output_file = os.path.join(out_file_path, output_file)
            if data_type=='uint8':
                dataset = driver.Create(output_file, x_size, y_size, in0.RasterCount, gdal.GDT_Byte)
            else:
                dataset = driver.Create(output_file, x_size, y_size, in0.RasterCount, gdal.GDT_Float32)
            for k, band in enumerate(bands, 1):
                if no_data_value is None:
                    no_data_value = band.GetNoDataValue()
                band_data = np.full((tile_y + buffer_size * 2, tile_x + buffer_size * 2), no_data_value, dtype=data_type)
                band_data[ys:ys+ymax, xs:xs+xmax] = band.ReadAsArray(xmin, ymin, xmax, ymax)
                dataset.GetRasterBand(k).WriteArray(band_data)
                dataset.GetRasterBand(k).SetNoDataValue(no_data_value)
            dataset.SetGeoTransform(trans2)
            dataset.SetProjection(proj)
            dataset.FlushCache()
            dataset = None
    in0 = None
    return


def raster_to_training_tiles(in_file, ref_file, out_file_path, tile_x=1000, tile_y=1000, buffer_size=12, data_type='float32', no_data_value=None):
    """
    Build tiled rasters. Produce tiles when having all valid pixels (valid only for north-up images)
    :param in_file: file name of the input virtual/actual raster files
    :param ref_file: file name of the reference raster to set up the tiles
    :param out_file_path: output path for tiles
    :param tile_x: width of each tile
    :param tile_y: height of each tile
    :param buffer_size: buffer_size of each tile (pixels added to top, bottom, left and right)
    :param data_type: data type: float32 -> gdal.GDT_Float32, uint8 -> gdal.GDT_Byte
    :param no_data_value: No-Data value
    :return: None
    """

    df0 = pd.DataFrame()
    ref_name = os.path.splitext(os.path.basename(ref_file))[0]
    in0 = gdal.Open(ref_file)
    gt0 = in0.GetGeoTransform()
    prj0 = in0.GetProjection()

    in1 = gdal.Open(in_file)
    gt1 = in1.GetGeoTransform()
    prj1 = in1.GetProjection()

    print('Total number of raster bands: ', in1.RasterCount)
    bands = []
    for band_num in range(in1.RasterCount):
        band_num += 1
        band = in1.GetRasterBand(band_num)
        bands.append(band)

    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    for i in range(0, in0.RasterXSize, tile_x):
        for j in range(0, in0.RasterYSize, tile_y):
            if no_data_value is None:
                no_data_value = bands[-1].GetNoDataValue()
            # for north-up images: simplified inversion of geolocation
            ulx = gt0[0] + (i-buffer_size) * gt0[1]
            uly = gt0[3] + (j-buffer_size) * gt0[5]
            lrx = gt0[0] + (i+tile_x+buffer_size) * gt0[1]
            lry = gt0[3] + (j+tile_x+buffer_size) * gt0[5]
            p0x = int((ulx - gt1[0]) / gt1[1])  # x pixel
            p0y = int((uly - gt1[3]) / gt1[5])  # y pixel
            p1x = int((lrx - gt1[0]) / gt1[1])  # x pixel
            p1y = int((lry - gt1[3]) / gt1[5])  # y pixel

            if p1x<1 or p1y<1 or p0x>=in1.RasterXSize or p0y>=in1.RasterYSize:
                continue
            xmin = max(0, p0x)
            xs = xmin - p0x
            x_size = p1x - p0x
            xmax = min(in1.RasterXSize - xmin, x_size - xs)
            ymin = max(0, p0y)
            ys = ymin - p0y
            y_size = p1y - p0y
            ymax = min(in1.RasterYSize - ymin, y_size - ys)
            band_data = np.full((y_size, x_size), no_data_value, dtype=data_type)
            band_data[ys:ys+ymax, xs:xs+xmax] = bands[-1].ReadAsArray(xmin, ymin, xmax, ymax)
            if no_data_value == band_data.max() or np.isnan(band_data.max()):
                continue

            trans1 = (ulx, gt1[1], gt1[2], uly, gt1[4], gt1[5])
            output_filename = '{}_tile_{}_{}_{}.tif'.format(ref_name, i, j, os.path.splitext(os.path.basename(in_file))[0])
            output_file = os.path.join(out_file_path, output_filename)
            if data_type=='uint8':
                dataset = driver.Create(output_file, x_size, y_size, in1.RasterCount, gdal.GDT_Byte)
            else:
                dataset = driver.Create(output_file, x_size, y_size, in1.RasterCount, gdal.GDT_Float32)
            for k, band in enumerate(bands, 1):
                if no_data_value is None:
                    no_data_value = band.GetNoDataValue()
                band_data = np.full((y_size, x_size), no_data_value, dtype=data_type)
                band_data[ys:ys+ymax, xs:xs+xmax] = band.ReadAsArray(xmin, ymin, xmax, ymax)
                dataset.GetRasterBand(k).WriteArray(band_data)
                dataset.GetRasterBand(k).SetNoDataValue(no_data_value)
            dataset.SetGeoTransform(trans1)
            dataset.SetProjection(prj1)
            dataset.FlushCache()
            dataset = None
            px = (ulx + lrx) / 2
            py = (uly + lry) / 2
            df0 = df0.append(
                {'ref_file': ref_name, 'filename': output_filename, 'x': px, 'y': py,
                 'size': os.path.getsize(output_file), 'class': 0},
                ignore_index=True)
    df0.to_csv(os.path.join(os.path.dirname(ref_file), '{}_tile_{}_table.csv'.format(ref_name, os.path.splitext(os.path.basename(in_file))[0])))
    in0 = None
    in1 = None
    return


def raster_to_tiles_translate(in_file, ref_file, out_file_path, tile_x=1000, tile_y=1000, buffer_size=12, data_type='Float32'):
    """
    Build tiled rasters based on geolocations using gdal_translate
    :param in_file: file name of the input virtual/actual raster files
    :param ref_file: file name of the reference raster to set up the tiles
    :param out_file_path: output path for tiles
    :param tile_x: width of each tile
    :param tile_y: height of each tile
    :param buffer_size: buffer_size of each tile (pixels added to top, bottom, left and right)
    :param data_type: data type: Byte/Int16/UInt16/UInt32/Int32/Float32/Float64
    :return: None
    """
    df0 = pd.DataFrame()
    ref_name = os.path.splitext(os.path.basename(ref_file))[0]
    in0 = gdal.Open(ref_file)
    gt = in0.GetGeoTransform()
    prj = in0.GetProjection()
    for i in range(0, in0.RasterXSize, tile_x):
        for j in range(0, in0.RasterYSize, tile_y):
            ulx = gt[0] + (i-buffer_size) * gt[1] + (j-buffer_size) * gt[2]
            uly = gt[3] + (i-buffer_size) * gt[4] + (j-buffer_size) * gt[5]
            lrx = gt[0] + (i+tile_x+buffer_size) * gt[1] + (j+tile_x+buffer_size) * gt[2]
            lry = gt[3] + (i+tile_x+buffer_size) * gt[4] + (j+tile_x+buffer_size) * gt[5]
            output_filename = '{}_tile_{}_{}_{}.tif'.format(ref_name, i, j, os.path.splitext(os.path.basename(in_file))[0])
            output_file = os.path.join(out_file_path, output_filename)
            gdal_expression = (
                'gdal_translate -ot {} -projwin {} {} {} {} '
                '-co COMPRESS=LZW -co PREDICTOR=2 "{}" "{}"').format(
                data_type, ulx, uly, lrx, lry, in_file, output_file)
            print(gdal_expression)
            subprocess.check_output(gdal_expression, shell=True)
            df0 = df0.append(
                {'ref_file': ref_name, 'filename': output_filename, 'size': os.path.getsize(output_file), 'class': 0},
                ignore_index=True)
    in0 = None
    df0.to_csv(os.path.join(out_file_path, '{}_tile_{}_table.csv'.format(ref_name, os.path.splitext(os.path.basename(in_file))[0])))
    return


def h5_to_csv(h5_file, csv_file, chunksize=50000):
    """
    Reformat stored hdf5 to csv.
    :param chunksize: number of lines
    :param h5_file:
    :param csv_file:
    :return:
    """
    if os.path.isfile(csv_file):
         os.remove(csv_file)
    for df in pd.read_hdf(h5_file, 'df0', chunksize=chunksize):
        if not os.path.isfile(csv_file):
            df.to_csv(csv_file, mode='a', index=False, header=True)
        else:
            df.to_csv(csv_file, mode='a', index=False, header=False)


def get_raster_extent(in0):
    """
    for every input in0
    return raster extent, and raster resolution
    """
    gt = in0.GetGeoTransform()
    xs = in0.RasterXSize
    ys = in0.RasterYSize
    x1 = gt[0] + 0 * gt[1] + 0 * gt[2]
    y1 = gt[3] + 0 * gt[4] + 0 * gt[5]
    x2 = gt[0] + xs * gt[1] + ys * gt[2]
    y2 = gt[3] + xs * gt[4] + ys * gt[5]
    extent0 = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
    res0 = [max(abs(gt[1]), abs(gt[4])), max(abs(gt[2]), abs(gt[5]))]
    return extent0, res0
