import six
import logging
import traceback
from redis import ConnectionError, TimeoutError
from datetime import datetime, timedelta, time
from eurodecorators.decorators import max_sim_execs
from .xmla import xmla
from lxml import etree
import requests

logger = logging.getLogger('eurotools')


class Cube(object):
    """
            This class is used to connnect with the cube, in that moment the dimensions and measures are calculated
            , and to launch queries against cube.

        **Attributes:**
            #. dimensiones: A dict, the keys are tuples with the name of the dimension first, in second place the attribute of this dimension and in third place 'All' (to explore all values of that attribute) or the attribute again to explore one to one . And the values are the dimension like is needed to create in a mdx .Example: dimensiones={('Client','Client','Client'):'[Client].[Client].[Client]'}
            #. medidas: As the attribute dimension but the keys are different only have two values, the first is 'Measures' for all them , and the second is the measure.Example: medidas={('Measures','Calls'):'[Measures].[Calls]'}
            #. connection: An instance of XMLAProvider after connected with the OLAP services, this attribute is needed to all methods which need the cube parameter.
            #. name: A string , the name of the database where is the cube.
            #. key_cache_dimYmed: A string which has the key to add and get the dimensiones and medidas attributes in memcache.
    """

    def __init__(self, limit_sim_exe=0, limit_time=0, version='0', timeout=2):
        self.limit_sim_exe = limit_sim_exe
        self.limit_time = limit_time
        self.__version__ = version
        self.dimensiones = {}
        self.medidas = {}
        self.connection = ''   # Es del tipo XMLASOURCE
        self.name_bbdd = ''
        self.key_cache_dimYmed = ''
        self.redis = ''
        self.ip = ''
        self.location = "http://{0}/OLAP/msmdpump.dll"
        self.timeout = timeout

    def _checkMachine(self):
        try:
            requests.get(self.location, timeout=self.timeout)
            return True
        except requests.ConnectionError:
            logger.error('OLAP Server {0} is not available. Error = {1}'.format(self.ip, traceback.format_exc()))
            return False

    def connect(self, ip, bbdd=[], cubes=[], redis=""):
        """
          **Description:**
                Create connection with OLAP services and get the dimension and medidas from the cubes which are in the databases that we want to connnect.
          **Args:**
                #. ip: A string with the IP of OLAP service.
                #. bbdd: A list of strings with the names of databases where are the cubes which we will use.
                #. bbdd: A list of strings with the names of cubes which we will use.
          **Returns:**
                An object like <olap.xmla.xmla.XMLASource object at 0xa7ae5ac> : it`s the connection with OLAP service
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        self.ip = ip
        self.location = self.location.format(self.ip)

        def addDimension_Medidas_redis(ide, value):
            try:
                if self.redis.get(ide) is None:
                    return self.redis.set(ide, value)
            except ConnectionError:
                logger.error('Connection error Redis adding dimension and measures: {0}'.format(traceback.format_exc()))
            except TimeoutError:
                logger.error('Timeout error Redis adding dimension and measures')
            return False

        def getDimension_Medidas_redis(ide):
            try:
                value = eval(self.redis.get(ide))
            except ConnectionError:
                logger.error('Connection error Redis get dimension and measures: {0}'.format(traceback.format_exc()))
                value = [{}, {}]
            except TimeoutError:
                logger.error('Timeout error Redis get dimension and measures')
                value = [{}, {}]
            return value[0], value[1]

        def isAdded_redis(ide):
            try:
                res = not (self.redis.get(ide) is None)
            except ConnectionError:
                logger.error('Connection error Redis adding dimension and measures: {0}'.format(traceback.format_exc()))
                res = False
            except TimeoutError:
                logger.error('Timeout error Redis adding dimension and measures')
                res = False
            return res
        if self._checkMachine():
            try:
                self.redis = redis
                p = xmla.XMLAProvider()
                self.connection = p.connect(location=self.location)
                if type(bbdd) is list:
                    bbdd = bbdd[0]
                self.name_bbdd = bbdd
                self.key_cache_dimYmed = self.name_bbdd + '_dimYmed'
                if not isAdded_redis(self.key_cache_dimYmed):
                    try:
                        self.medidas = self._getMedidas(bbdd)
                        self.dimensiones = self._getDimensiones(bbdd)
                        value = []
                        value.append(self.medidas)
                        value.append(self.dimensiones)
                        addDimension_Medidas_redis(self.key_cache_dimYmed, value)
                    except Exception:
                        logger.error('Error setting measures and dimensions in redis: {0}'.format(traceback.format_exc()))
                else:
                    self.medidas, self.dimensiones = getDimension_Medidas_redis(self.key_cache_dimYmed)
            except:
                logger.error('Error connecting cube.Error = {0}'.format(traceback.format_exc()))
                raise
            return self.connection
        else:
            return False

    def _getDimensiones(self, bbdd=['NO_CUBE_DB_NAME_IN_SETTINGS']):

        dimensiones = {}
        catalogs = self.connection.getCatalogs()
        for catalogo in catalogs:
            if catalogo.getUniqueName() == bbdd:
                for Cube in catalogo.getCubes():
                    for dim in Cube.getDimensions():
                        for jerar in dim.getHierarchies():
                            for level in jerar.getLevels():
                                name = level.getUniqueName()
                                first_name = name[name.find('[') + 1:name.find(']')]
                                name_aux = name[name.find(']') + 1:]
                                second_name = name_aux[name_aux.find('[') + 1:name_aux.find(']')]
                                name_aux = name_aux[name_aux.find(']') + 1:]
                                third_name = name_aux[name_aux.find('[') + 1:name_aux.find(']')]
                                third_name = third_name.replace('(', '').replace(')', '')
                                dimensiones[(first_name, second_name, third_name)] = level.getUniqueName()
        return dimensiones

    def name_dimension(self, axis, complete_name, col_cube_map={}):
        """
          **Description:**
                This method changes the name of dimension from the cubes understand to more readable.
          **Args:**
                #. axis: A list of string which represents a set of dimensions of the cube.
                #. complete_name: A boolean , if it is false return only the name of the dimension , in othre case return the name of the dimension and the attribute , separated by a comma.
          **Returns:**
                A lis of strings whit the names of the dimensions more readable to the human.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        if self.dimensiones:
            nombres = []
            for dimension in axis:
                if col_cube_map:
                    dimension2 = tuple(dimension.replace('[', '').replace(']', '').split('.'))
                    if dimension2 not in col_cube_map:
                        nombres.append(dimension)
                    else:
                        nombres.append(col_cube_map[dimension2])
                else:
                    for dim in self.dimensiones:
                        if self.dimensiones[dim] == dimension:
                            if not complete_name:
                                dim = str(dim[0])
                                nombres.append(dim)
                            else:
                                dim = str(dim[0]) + '*' + str(dim[1])
                                nombres.append(dim)
            return nombres
        else:
            self.redis.delete(self.key_cache_dimYmed)
            return 'cube has not dimensions or it is not good connect'

    def _getMedidas(self, bbdd=['NO_CUBE_DB_NAME_IN_SETTINGS']):
        medidas = {}
        catalogs = self.connection.getCatalogs()
        for catalogo in catalogs:
            if catalogo.getUniqueName() == bbdd:
                for Cube in catalogo.getCubes():
                    for medida in Cube.getMeasures():
                        name = medida.getUniqueName()
                        first_name = name[name.find('[') + 1:name.find(']')]
                        name_aux = name[name.find(']') + 1:]
                        second_name = name_aux[name_aux.find('[') + 1:name_aux.find(']')]
                        name_aux = name_aux[name_aux.find(']') + 1:]
                        medidas[(first_name, second_name)] = name
        return medidas

    def _get_decorator_params(self):
        return self.name_bbdd + '_MAX_SIM_EXECS_' + self.ip, self.limit_sim_exe, self.redis, self.limit_time

    @max_sim_execs()
    def launch_query(self, mdx=None):
        """
          **Description:**
                This method launch a query against the cube and return the result in xml format.
          **Args:**
                mdx: A string which represents the mdx to launch against the cube
          **Returns:**
                A xml object which has the result to make the query
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        if self._checkMachine():
            self.connection.client.set_options(retxml=True)
            result = self.connection.Execute(mdx, Catalog=self.name_bbdd)
            self.connection.client.set_options(retxml=False)
            return result
        else:
            return False


class XmlResult(object):
    """
            This class is used to get the values from the xml which got from launch a mdx against the cube.

        **Attributes:**
            Nothing.
    """

    def __init__(self, format_dim=None):
        self.format_dim = format_dim 

    def returnEmpty(self, error):
        axis_x_names = ''
        axis_y_names = ''
        axis_x_values = []
        axis_y_values = []
        numero_filas = 0
        numero_dimensiones = 0
        numero_celdas = 0
        numero_medidas = 0
        return (axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error)

    def getValues(self, xml1, format_cube=False):
        """
          **Description:**
                This method is to get the values from xml which is the result from launch a mdx against the cube.
          **Args:**
                xml1: A xml which represents the result to launch a mdx against the cube
          **Returns:**
                #. A tuple with 8 elements:
                        #. axis_x_names: A list of strings which have the names of the measures used.
                        #. axis_y_names: A list of strings which have the names of the dimensions used.
                        #. axis_x_values: A list of strings which have the values of the measures used.
                        #. axis_y_values: A list of strings which have the names of the dimensions used.
                        #. numero_filas: An integer which represents the number of rows returns from the cube.
                        #. numero_dimensiones:  An integer which represents the number of dimensions used.
                        #. numero_celdas: A integer which represents the numbers of values returns of all measures.
                        #. numero_medidas: An integer which represents the number of measures used.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
        # Name space
        NS = '{urn:schemas-microsoft-com:xml-analysis:mddataset}'
        # Cast to bytes
        if not xml1:
            error = 'cube has not dimensions or it is not good connect'
            return self.returnEmpty(error)
        else:
            if six.PY3 and isinstance(xml1, bytes):
                xml1 = xml1.decode("utf-8")
        if xml1.find('faultcode') > 0 or xml1.find('ErrorCode') > 0:
            if xml1.find('faultcode') > 0:
                error = xml1[xml1.find('<faultstring>') + 13:xml1.find('</faultstring>')]
            else:
                error = xml1[xml1.find('Error') + 5:]
            return self.returnEmpty(error)
        else:
            try:
                xml = etree.fromstring(xml1)
                axes = xml.find('.//{0}Axes'.format(NS))
            except:
                logger.error('Cube returned error: {0} {1}'.format(traceback.format_exc(), xml1))
                return self.returnEmpty('Connection Error')
            if len(axes.getchildren()) > 1:
                axis_y = axes.getchildren()[1]
                numero_filas = len(axis_y.getchildren()[0].getchildren())
                if numero_filas == 0:
                    return self.returnEmpty(False)

                complete_y_names = False
                numero_dimensiones = len(axis_y.getchildren()[0].getchildren()[0].getchildren())
                # Detect hierarchy descendants (if there is one dimension (hierarchy) and member unique_name (UName) has hierarchy levels (UName has more elements than hierarchy_attrib+1))
                if numero_dimensiones == 1:
                    member = axis_y.find('.//{0}Member'.format(NS))
                    member_attr = member.get('Hierarchy')
                    member_name = member.find('.//{0}UName'.format(NS)).text
                    if len(member_name.split('.')) > len(member_attr.split('.')) + 1:
                        complete_y_names = True

                if complete_y_names:
                    axis_y_names = [i.text for i in axis_y.findall('.//{0}LName'.format(NS))]
                else:
                    axis_y_names = [axis_y.findall('.//{0}Member'.format(NS))[i].find('.//{0}LName'.format(NS)).text for i in range(0, numero_dimensiones)]

                # axis_y_values = [i.text for i in axis_y.findall('.//{0}Caption'.format(NS))]
                # Get correct value from UName when Caption is None (value could be '' or 0 (null))
                axis_y_values = []
                for i in axis_y.findall('.//{0}Member'.format(NS)):
                    value = i.find('.//{0}Caption'.format(NS)).text
                    if value is None:
                        value = i.find('.//{0}UName'.format(NS)).text.split('.&[')[-1][:-1]
                    axis_y_values.append(value)

                axis_x = axes.getchildren()[0]
                axis_x_names = [i.text for i in axis_x.findall('.//{0}Caption'.format(NS))]
                numero_medidas = len(axis_x_names)
                error = False
                celdas = xml.find('.//{0}CellData'.format(NS)).getchildren()
                if len(celdas) > 0:
                    axis_x_values = self.getAxisXValues(celdas, NS, format_cube)
                else:
                    axis_x_values = []
                numero_celdas = len(axis_x_values)
                self.appplyFormatDims(axis_y_names, axis_y_values)
                return (axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error)
            else:
                numero_filas = 1
                numero_dimensiones = 0
                axis_y_names = []
                axis_y_values = []
                axis_x = axes.getchildren()[0]
                axis_x_names = [i.text for i in axis_x.findall('.//{0}Caption'.format(NS))]
                numero_medidas = len(axis_x_names)
                error = False
                celdas = xml.find('.//{0}CellData'.format(NS)).getchildren()
                if len(celdas) > 0:
                    axis_x_values = self.getAxisXValues(celdas, NS, format_cube)
                else:
                    axis_x_values = []
                numero_celdas = len(axis_x_values)
                return (axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error)


    def appplyFormatDims(self, axis_y_names, axis_y_values):
        if self.format_dim:
            names_set = set(axis_y_names)
            formats_dim = set(self.format_dim.keys())
            if formats_dim.intersection(names_set):
                for index, val in enumerate(axis_y_names * int(len(axis_y_values) / len(axis_y_names))):
                    if val in self.format_dim:
                        axis_y_values[index] = datetime.strptime(axis_y_values[index], self.format_dim[val][0]).strftime(self.format_dim[val][1])
        

    def getAxisXValues(self, celdas, NS, format_cube):
        if format_cube:
            find = './/{0}FmtValue'
        else:
            find = './/{0}Value'
        find_ns = find.format(NS)
        do_format = find == './/{0}Value'
        axis_x_values_dict = {}
        for celda in celdas:
            key = int(celda.get('CellOrdinal'))
            cell_select = celda.find(find_ns)
            if cell_select.text is not None:
                value = cell_select.text
                if do_format and cell_select.values():
                    cast_type = cell_select.values()[0].replace('xsd:', '')
                    cast = self.dameCast(cast_type)
                    axis_x_values_dict[key] = cast(value)
                else:
                    axis_x_values_dict[key] = value
        axis_x_values_final = []
        for i in range(0, int(celdas[len(celdas) - 1].get('CellOrdinal')) + 1):
            try:
                axis_x_values_final.append(axis_x_values_dict[i])
            except:
                axis_x_values_final.append('----')
        return axis_x_values_final

    def dameCast(self, cast_type):
        if cast_type == 'double':
            return float
        else:
            return int


class Format(object):
    """
            This class is used to get differents format to filters, highcharts ...

        **Attributes:**
            Nothing.

    """
    def __init__(self, format_dim=None):
        self.format_dim = format_dim 

    def replaceSimbols(self, value, format_cube):
        if value == '----':
            value = '0'
        if format_cube:
            return value
        value = str(value).replace('%', '')
        value = str(value).replace('$', '')
        value = str(value).replace('', '')
        return float(value)

    def dict(self, cube, result, complete_name=False, format_cube=False):
        """
          **Description:**
                This function is used to get one filter acording to the mdx which we have used.
          **Args:**
                #. query: A string which is a mdx
                #. cube: The cube object which has been used
                #. dimensiones: A string with the dimension which calculate the mdx to get the filter.
                #. database_cube_dict: A dict with the names of the dimension which the cube returns and the names that we want.
                #. exclude_rows: A dict with the name of a dimension and like value that we want to exclude from the filters.
          **Returns:**
                A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
          **Modify:**
                Non modify anything
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """
        xml_class = XmlResult(self.format_dim)
        axis_x_names, axis_y_names, axis_x_values, axis_y_values, numero_filas, numero_dimensiones, numero_celdas, numero_medidas, error = xml_class.getValues(result, format_cube)
        list_result = []
        if numero_dimensiones == len(axis_y_names):
            for fila in range(0, numero_filas):
                item = {}
                for dimension in range(0, numero_dimensiones):
                    act = (fila * numero_dimensiones) + dimension
                    item[axis_y_names[dimension]] = axis_y_values[act]

                for medida in range(0, numero_medidas):
                    act = (fila * numero_medidas) + medida
                    try:
                        item[axis_x_names[medida]] = axis_x_values[act]
                    except:
                        item[axis_x_names[medida]] = 0
                list_result.append(item)
        else:
            # Different number of dimensions (one) and axis_y_names (Hierarchy case)
            for fila in range(0, numero_filas):
                item = {}
                item[axis_y_names[fila]] = axis_y_values[fila]

                for medida in range(0, numero_medidas):
                    act = (fila * numero_medidas) + medida
                    try:
                        item[axis_x_names[medida]] = axis_x_values[act]
                    except:
                        item[axis_x_names[medida]] = 0
                list_result.append(item)
        return list_result


class Mdx(object):

    """
            This class is used to create mdx to launch against the cube.
        **Attributes:**
            Nothing.

    """
    def __init__(self, dim_date= [('Date', 'Id', 'Id')], dim_time=('Time', 'Time Field', 'Time Field'), format_date_in='%Y%m%d%H%M%S', format_date_out='%Y%m%d', format_time_out='%H%M', only_date=False):
        self.dim_date = dim_date
        self.dim_time = dim_time
        self.format_date_in = format_date_in
        self.format_date_out = format_date_out
        self.format_time_out = format_time_out
        self.only_date = only_date

    def __non_empty(self, part_NON_EMPTY):
        if part_NON_EMPTY:
            return ' non empty '
        else:
            return' '

    def __extract_date_info(self, part, part_filter):
        date_info = {}
        dim_to_remove = []
        for dim in part_filter:
            if dim in self.dim_date and type(part_filter[dim]) is tuple:
                date_info[dim] = part_filter[dim]
                dim_to_remove.append(dim)

        for dim in dim_to_remove:
            part.remove(dim)
            del(part_filter[dim])

        return date_info

    def __rows_or_columns(self, cube, rows, part=[], range_rows={}, exclude_rows={}, part_order={}, part_filter={}):
        dimensiones = cube.dimensiones
        medidas = cube.medidas
        order = ''
        for i in part_order:
            if i in dimensiones:
                order = 'dim'
            elif i in medidas:
                order = 'med'
            else:
                order = 'null'
        mdx = ''
        if part_order and order == 'dim':
            part.remove(list(part_order.keys())[0])
            part.insert(0, list(part_order.keys())[0])
        if order != 'dim':
            if part_order and order != 'null':
                if part_order[list(part_order.keys())[0]] == 'ASC' or part_order[list(part_order.keys())[0]] == 'BASC':
                    mdx += 'bottomcount('
                else:
                    mdx += 'topcount('
        if part:
            if rows:
                mdx += ' ( '
                self.__change_date_format(part_filter)
                date_on_row = self.__where_dict_date(cube, self.__extract_date_info(part, part_filter))
                if date_on_row:
                    mdx += date_on_row + ','
            else:
                mdx += ' { '

            for i in range(0, len(part)):
                on_row = part[i]
                if on_row in dimensiones:
                    if on_row in range_rows:
                        position = dimensiones[on_row].find('.') + 1
                        dim = dimensiones[on_row][position:]
                        position += dim.find('.') + 1
                        mdx += dimensiones[on_row][:position] + self._getFilterElement(str(range_rows[on_row][0])) + ':'
                        mdx += dimensiones[on_row][:position] + self._getFilterElement(str(range_rows[on_row][1]))
                        if on_row in exclude_rows:
                            for dim in exclude_rows[on_row]:
                                mdx += '-' + dimensiones[on_row][:position] + self._getFilterElement(dim)
                        mdx += ','
                    elif on_row not in part_filter:
                        position = dimensiones[on_row].find('.') + 1
                        dim = dimensiones[on_row][position:]
                        position += dim.find('.') + 1
                        mdx += dimensiones[on_row]
                        for exclude in exclude_rows:
                            if on_row in exclude:
                                mdx += '-' + dimensiones[on_row][:position] + self._getFilterElement(str(exclude[on_row]))
                        mdx += ','
                elif on_row in medidas:
                    mdx += medidas[on_row] + ','
                else:
                    logger.error('Failed MDX class 2 : on_row is not in measures neither dimensions')
                    mdx += '<<error in {0} >>'.format(str(on_row))
            mdx = mdx[0:len(mdx) - 1]
            for fil in part_filter:
                if fil in dimensiones:
                    position = dimensiones[fil].find('.') + 1
                    dim = dimensiones[fil][position:]
                    position += dim.find('.') + 1
                    if len(part) == 1:
                        mdx_aux = '{'
                    else:
                        mdx_aux = ',{'
                    for i in range(0, len(part_filter[fil])):
                        mdx_aux += dimensiones[fil][:position] + self._getFilterElement(str(part_filter[fil][i])) + ','
                    mdx += mdx_aux[:-1] + '}'

            # Remove comma when It is after all the dimensions
            mdx = mdx.replace('(,{[', '({[')
            if rows:
                mdx += ') '
            else:
                mdx += '} '
            if part_order and order == 'dim':
                mdx = mdx
            elif part_order and order == 'med':
                medida = list(part_order.keys())[0]
                medida_mdx = '[' + str(medida[0]) + ']' + '.[' + str(medida[1]) + ']'
                mdx += ',100000000,' + medida_mdx + ')'

        return mdx

    def __partDate(self, cube, part_where, from_to, dim_date):

        """
          **Description:**
                This function is used to create the part where when we use date and time dimension.
          **Args:**
                #. part_where: A list that contain al the data need to create the where
                #. fecha:  A string which contain the date that we used.
                #. cube: The cube object which has been used
          **Returns:**
                Part of the where of a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information :

        """
        mdx = ''
        same_day = False
        same_day = part_where[dim_date][0].date() == part_where[dim_date][1].date()
        dim = '[' + dim_date[0] + '].[' + dim_date[1] + ']'
        mdx += '(' + dim + '.&[' + part_where[dim_date][from_to].strftime(self.format_date_out) + '] ) *'
        dim = '[' + self.dim_time[0] + '].[' + self.dim_time[1] + ']'
        if not same_day:
            if from_to == 0:
                mdx += '(' + dim + '.&[' + part_where[dim_date][from_to].strftime(self.format_time_out) + '] : ' + dim + '.&[2359]) *'
            else:
                mdx += '(' + dim + '.&[0] : ' + dim + '.&[' + part_where[dim_date][from_to].strftime(self.format_time_out) + ']) *'
        else:
            mdx += '(' + dim + '.&[' + str(int(part_where[dim_date][0].strftime(self.format_time_out))) + '] : ' + dim + '.&[' + str(int(part_where[dim_date][1].strftime(self.format_time_out))) + ']) *'
        mdx = mdx[:-1]
        return mdx

    def __partComplete(self, cube, part_where, set_time, dim_date):
        """
          **Description:**
                This function is used to create the part where when we use data dimension.
          **Args:**
                #. part_where: A list that contain al the data need to create the where
                #. nuevas_fechas:  A list of string which contain the dates that we used.
                #. cube: The cube object which has been used
          **Returns:**
                Part of the where of a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information :

        """
        mdx = ''
        dim = '[' + dim_date[0] + '].[' + dim_date[1] + ']'
        mdx += '(' + dim + '.&[' + part_where[dim_date][0].strftime(self.format_date_out) + '] : ' + dim + '.&[' + part_where[dim_date][1].strftime(self.format_date_out) + '])'
        if set_time:
            dim_time = '[' + self.dim_time[0] + '].[' + self.dim_time[1] + ']'
            mdx += ' * (' + dim_time + '.&[' + str(int(part_where[dim_date][0].strftime(self.format_time_out))) + '] : ' + dim_time + '.&[' + str(int(part_where[dim_date][1].strftime(self.format_time_out))) + '])'
        return mdx

    def _getFilterElement(self, element):
        if element == 'Unknown':
            elem = '[' + str(element) + ']'
        else:
            elem = '&[' + str(element) + ']'
        return elem

    def partRest(self, cube, part_where):
        mdx = ''
        for i in part_where:
            if i in cube.dimensiones:
                dim = '[' + i[0] + '].[' + i[1] + ']'
                if type(part_where[i]) is str or type(part_where[i]) is int:
                    part_where_aux = part_where[i]
                    if type(part_where[i]) in [str]:
                        part_where_aux = part_where[i].split(',')
                    if type(part_where[i]) is int:
                        part_where_aux = [part_where[i]]
                    mdx += ',{'
                    for one in part_where_aux:
                        mdx += dim + '.' + self._getFilterElement(one) + ','
                    mdx = mdx[0:-1]
                    mdx += '}'
                elif (type(part_where[i]) is tuple or type(part_where[i]) is list):
                    if part_where[i][0] == '-' and type(part_where[i][1]) == list:
                        exclude = ''
                        for n in part_where[i][1]:
                            exclude = exclude + str(part_where[i][0]) + dim + '.' + self._getFilterElement(n) + ' '
                        mdx += ',{(' + dim + '.' + '[' + str(i[2]) + ']' + exclude + ' )}'
                    else:
                        mdx += ',{'
                        for n in part_where[i]:
                            mdx += '(' + dim + '.' + self._getFilterElement(n) + ' ),'
                        mdx = mdx[:-1]
                        mdx += '}'
        return mdx

    def __where_dict(self, cube, part_where):
        mdx = ''
        mdx = self.__where_dict_date(cube, part_where)
        part_rest = self.partRest(cube, part_where)
        if not(mdx) and part_rest:
            part_rest = part_rest[1:]
        mdx += part_rest
        return ' ( ' + mdx + ' ) '

    def __where_dict_date(self, cube, part_where):
        mdx = ''
        for dim_date in self.dim_date:
            if dim_date in part_where and type(part_where[dim_date]) is tuple:
                time_from = int(part_where[dim_date][0].time().strftime(self.format_time_out)) == 0
                time_to = int(part_where[dim_date][1].time().strftime(self.format_time_out)) == 2359
                if (time_from and time_to) or self.only_date:
                    mdx += '{' + self.__partComplete(cube, part_where, False, dim_date) + '}, '
                else:
                    if part_where[dim_date][0].date() == part_where[dim_date][1].date():
                        mdx += '{' + self.__partDate(cube, part_where, 0, dim_date) + '}, '
                    else:
                        if not time_from:
                            mdx += '{' + self.__partDate(cube, part_where, 0, dim_date) + '}  + '
                            part_where[dim_date][0] = datetime.combine(part_where[dim_date][0] + timedelta(days=1), time.min)

                        if not time_to:
                            mdx += '{' + self.__partDate(cube, part_where, 1, dim_date) + '}  + '
                            part_where[dim_date][1] = datetime.combine(part_where[dim_date][1] - timedelta(days=1), time.max)

                        if not(part_where[dim_date][0] > part_where[dim_date][1]):
                            mdx += '{' + self.__partComplete(cube, part_where, True, dim_date) + '}, '
                        else:
                            mdx = mdx[:-1]
                del(part_where[dim_date])
        mdx = mdx[:-2]
        return mdx

    def __part_order(self, cube, part_on_rows, range_rows, exclude_rows, part_order, part_filter):
        mdx = ''
        for order in part_order:
            if part_order[order] == 'ASC' or part_order[order] == 'DESC' or part_order[order] == 'BASC' or part_order[order] == 'BDESC':
                mdx += self.__rows_or_columns(cube, True, part_on_rows, range_rows, exclude_rows, part_order, part_filter)
            else:
                mdx += self.__rows_or_columns(cube, True, part_on_rows, range_rows, exclude_rows, part_filter=part_filter)
        return mdx

    def __on_row(self, cube, part_on_rows, range_rows, exclude_rows, part_order, part_filter):
        mdx = ''
        if part_order:
            if len(part_order) == 1:
                mdx += self.__part_order(cube, part_on_rows, range_rows, exclude_rows, part_order, part_filter)
            else:
                logger.error('Failed MDX class 5 : try to order by more than two dimensions')
                mdx += '<< part_order must be like {0}>>'.format(str({('Measures', 'Calls'): 'ASC'}))
        else:
            mdx += self.__rows_or_columns(cube, True, part_on_rows, range_rows, exclude_rows, part_filter=part_filter)
        return mdx

    def __with_set_member_part(self, cube, part_rows=[], part_ranking=[]):
        mdx = ''
        mdx += 'WITH SET orderedDimension as topcount([' + part_rows[0][0] + '].[' + part_rows[0][1] + '].[' + part_rows[0][2] + '].members,100000000,[' + part_ranking[2][0] + '].[' + part_ranking[2][1] + '])'
        mdx += ' MEMBER ranking_medida as RANK([' + part_rows[0][0] + '].[' + part_rows[0][1] + '].CurrentMember,orderedDimension)'
        return mdx

    def __select_rank(self, cube, part_rows=[], part_ranking=[]):
        mdx = ''
        mdx += 'select '
        if part_ranking[0] == "ASC" or part_ranking[0] == "BASC":
            mdx += 'bottomcount('
        else:
            mdx += 'topcount('
        mdx += 'orderedDimension,' + part_ranking[1] + ') on rows,'
        return mdx

    def __mdx_rank(self, cube, part_rows=[], part_columns=[], part_ranking=[], range_rows=[], exclude_rows=[]):
        mdx = ''
        mdx += self.__with_set_member_part(cube, part_rows, part_ranking)
        mdx += self.__select_rank(cube, part_rows, part_ranking)
        mdx += self.__rows_or_columns(cube, False, part_columns, range_rows, exclude_rows)
        mdx += ' on columns'
        return mdx

    def __select_with_member_descendants(self, cube, part_hierarchy={}):
        mdx = ''
        if part_hierarchy['properties']:
            mdx += 'with '
            for property_name in part_hierarchy['properties']:
                mdx += ' member [Measures].[Property{0}] as [{1}].[{2}].Currentmember.Properties("{0}")'.format(property_name, part_hierarchy['hierarchy'][0], part_hierarchy['hierarchy'][1])
        mdx += ' select {'
        for property_name in part_hierarchy['properties']:
            mdx += ' [Measures].[Property{0}],'.format(property_name, part_hierarchy['hierarchy'][0], part_hierarchy['hierarchy'][1])
        mdx = mdx[:-1]
        mdx += '} on columns, '
        return mdx

    def __rows_descendants(self, cube, part_hierarchy={}):
        mdx = '{ filter('
        mdx += ' descendants([{0}].[{1}], [{0}].[{1}].Level, after), ('.format(part_hierarchy['hierarchy'][0], part_hierarchy['hierarchy'][1])
        for measure in part_hierarchy['measure_to_filter']:
            mdx += ' not IsEmpty([{0}].[{1}]) or'.format(measure[0], measure[1])
        mdx = mdx[:-2]
        mdx += ' ) ) } on rows'
        return mdx

    def __mdx_descendants(self, cube, part_hierarchy={}):
        mdx = ''
        mdx += self.__select_with_member_descendants(cube, part_hierarchy)
        mdx += self.__rows_descendants(cube, part_hierarchy)
        return mdx

    def __drill_down_member(self, cube, part_hierarchy={}):
        member = part_hierarchy['drill_down_member']
        mdx = 'drilldownmember([{0}].[{1}].[{2}].&[{3}].Children, {{}})'.format(member[0], member[1], member[2], member[3])
        return mdx

    def __drill_down_additional_rows(self, cube, part_rows=[], range_rows={}, exclude_rows=[], part_order={}, part_filter={}, part_hierarchy={}):
        mdx = ''
        # Remove upper hierarchy levels and drill down member from additional rows
        hierarchy_dim = part_hierarchy['hierarchy_dimensions']
        rows_to_exclude = hierarchy_dim[:hierarchy_dim.index(part_hierarchy['drill_down_member'][2])+2]
        additional_part_rows = []
        for row in part_rows:
            if row[2] not in rows_to_exclude or row[0] != part_hierarchy['drill_down_member'][0]:
                additional_part_rows.append(row)
        if len(additional_part_rows) > 0:
            mdx += ', '
            mdx += self.__on_row(cube, additional_part_rows, range_rows, exclude_rows, part_order, part_filter)
        return mdx

    def __mdx_drill_down(self, cube, part_rows=[], part_columns=[], range_rows={}, exclude_rows=[], part_order={}, part_filter={}, part_NON_EMPTY=True, part_hierarchy={}):
        mdx = 'select {0} ('.format(self.__non_empty(part_NON_EMPTY))
        mdx += self.__drill_down_member(cube, part_hierarchy=part_hierarchy)
        mdx += self.__drill_down_additional_rows(cube, part_rows, range_rows, exclude_rows, part_order, part_filter, part_hierarchy=part_hierarchy)
        mdx += ' ) on rows, '
        mdx += self.__rows_or_columns(cube, False, part_columns, range_rows, exclude_rows)
        mdx += ' on columns'
        return mdx

    def __mdx_hierarchy(self, cube, part_rows=[], part_columns=[], range_rows={}, exclude_rows=[], part_order={}, part_filter={}, part_NON_EMPTY=True, part_hierarchy={}):
        if part_hierarchy['drill_down_member']:
            mdx = self.__mdx_drill_down(cube, part_rows=part_rows, part_columns=part_columns, range_rows=range_rows, exclude_rows=exclude_rows, part_order=part_order, part_filter=part_filter, part_NON_EMPTY=part_NON_EMPTY, part_hierarchy=part_hierarchy)
        else:
            mdx = self.__mdx_descendants(cube, part_hierarchy=part_hierarchy)
        return mdx

    def mdx(self, cube, part_rows=[], range_rows=[], exclude_rows={}, part_columns=[], part_from='', part_where={}, part_order=[], part_NON_EMPTY=True, part_ranking=[], part_hierarchy={}):

        """
          **Description:**
                This function is used to create the mdx which we will use to launch against the cube.
          **Args:**
                #. cube: An object cube which we have used to create the connection.
                #. part_rows: A list of tuples with three values to indicate the dimension to browse : [('client','client','client'),('client','id','all'),...]
                #. range_rows: A dict where we put the dimension which we want aplicate the range and like value the values of the range.
                #. exclude_rows: A list of dict for the columns and value to exclude: [{('client','client'):2345},{('client','id'):...}]
                #. part_columns: A list of tuples for the columns to indicate the measures to browse: [('Measure','Calls'),('Measure','Attempts'),...]
                #. part_from  A string with the name of the cube :'[stoneworksolutions dev]'
                #. part_where:  A dict. The key is the dimension and the value is the value which want put in the where :{('client','client'):'Aryans',('cdrfint','fecha'):('2013101010101010','2013101110101010')....}
                #. part_order: A dict with only one key.The key is the measure or dimension to order and the value indicate the order to do, it can be('ASC','DESC','BASC','BDESC') :{('measure','calls'):'ASC'}

                #. part_NON_EMPTY: A booleann that indicate if is True that we want the clausule 'non empty' in the mdx , by contrast we don`t want non empty in the mdx
                #. part_ranking: A list with differents values. An example is part_rank=["ASC","10",('Measure','Calls')]. The first value indicates how we want the order, the second how many rows will be return and the third the measure on which will do the ranking.
                #. part_hierarchy: A dict with hierarchy information ('properties' key is optional, drill_down_member (tuple of 4 elements) and hierarchy_dimensions (list) are related to drill down member. Example: part_hierarchy={'hierarchy': ('Destinations', 'DestinationsHierarchy'), 'measure_to_filter': ('Measures', 'Cost'), 'properties': ['Key', 'Name'], 'drill_down_member': None, 'hierarchy_dimensions': []}


                # EXAMPLESSSSSSSS
                # from sws_tags.sws_utils.cube_utils import *
                # mdx=MDX()
                # cube=CUBE()
                # cube.connect('apollo','sultan2014',['Cdrt','ChannelUSage'],redis_conn)
                # where={('Date','Day Complete','Day Complete'):('20140812000000','20140822235959'),('Provider','Id','Id'):['1','120']}
                # columns=[('Measures','Total Cost'),('Measures','Usd Total Cost')]
                # mdx.mdx(cube,part_columns=columns,part_from='[Cdrt]',part_where=where)

                # where={('Date','Day Complete','Day Complete'):['20140812000000','20140822235959','20141022235959'],('Provider','Id','Id'):['1','120']}
                # columns=[('Measures','Total Cost'),('Measures','Usd Total Cost')]
                # rows=[('Provider','Id','Id')]
                # mdx.mdx(cube,part_rows=rows,part_columns=columns,part_from='[Cdrt]',part_where=where)

                # where={('Date','Day Complete','Day Complete'):['20140812000000','20140822235959'],('Provider','Id','Id'):['1','120']}
                # columns=[('Measures','Total Cost'),('Measures','Usd Total Cost')]
                # rows=[('Provider','Id','Id'),('Client','Id','Id')]
                # mdx.mdx(cube,part_rows=rows,part_columns=columns,part_from='[Cdrt]',part_where=where)

                # where={('Date','Day Complete','Day Complete'):['20140812000000','20140822235959'],('Provider','Id','Id'):['1','120']}
                # columns=[('Measures','Total Cost'),('Measures','Usd Total Cost')]
                # rows=[('Destination','Id','Id'),('Provider','Id','Id'),('Client','Id','Id')]
                # mdx.mdx(cube,part_rows=rows,part_columns=columns,part_from='[Cdrt]',part_where=where)

          **Returns:**
                This function return a string which is a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
              Nothing.
          Other information ::


        """
        # MIRAR SI EN SELECT Y EN WHERE ESTA LA MISMA DIMENION DE SER ASI DEJARLA SOLO EL SELECT Y UTILIZAR FILTER
        part_filter = {}
        part_rows = self.quitarDuplicados(part_rows)
        part_filter, part_where = self.__whereInSelect(part_where, part_rows, part_filter)
        mdx = ''
        if cube.dimensiones:
            if part_ranking:
                mdx = self.__mdx_rank(cube, part_rows=part_rows, part_columns=part_columns, part_ranking=part_ranking, range_rows=range_rows, exclude_rows=exclude_rows)
            elif part_hierarchy:
                mdx = self.__mdx_hierarchy(cube, part_rows=part_rows, part_columns=part_columns, range_rows=range_rows, exclude_rows=exclude_rows, part_order=part_order, part_filter=part_filter, part_NON_EMPTY=True, part_hierarchy=part_hierarchy)
            else:
                mdx = 'select'
                mdx += self.__non_empty(part_NON_EMPTY)
                if len(part_rows) > 0:
                    mdx += self.__on_row(cube, part_rows, range_rows, exclude_rows, part_order, part_filter)
                    mdx += 'on rows, '
                mdx += self.__rows_or_columns(cube, False, part_columns, range_rows, exclude_rows)
                mdx += ' on columns'
            if part_where:
                self.__change_date_format(part_where)
                mdx += ' from (select '
                mdx += self.__where_dict(cube, part_where)
                mdx += ' on columns from ' + part_from + ' ) '
            else:
                mdx += ' from ' + part_from
            return mdx
        else:
            logger.error('Failed MDX 7 class : cube has not dimensions or it is not good connect')
            return 'cube has not dimensions or it is not good connect'

    def __change_date_format(self, part_where):
        for dim_date in self.dim_date:
            if dim_date in part_where:
                if not type(part_where[dim_date][0]) is datetime:
                    if type(part_where[dim_date]) is tuple:
                        part_where[dim_date] = (datetime.strptime(part_where[dim_date][0], self.format_date_in), datetime.strptime(part_where[dim_date][1], self.format_date_in))


    def quitarDuplicados(self, col_cube):
        new_col_cube = []
        for i in col_cube:
            if i not in new_col_cube:
                new_col_cube.append(i)
        return new_col_cube

    def __whereInSelect(self, part_where, part_rows, part_filter):
        dimensiones = []
        for i in part_where:
            for j in part_rows:
                if i == j:
                    dimensiones.append(i)
        return self.__quitar_where_poner_filter(dimensiones, part_where, part_filter)

    def __quitar_where_poner_filter(self, dimensiones, part_where, part_filter):
        new_filter = {}
        for dimension in dimensiones:
            valor_filter = part_where[dimension]
            del part_where[dimension]
            if isinstance(valor_filter, list):
                # Remove duplicated values
                new_filter[dimension] = list(set(valor_filter))
            elif isinstance(valor_filter, tuple) and dimension in self.dim_date:
                new_filter[dimension] = valor_filter
            else:
                new_filter[dimension] = [valor_filter]
        return new_filter, part_where
