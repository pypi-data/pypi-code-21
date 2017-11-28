# coding: utf-8
"""
    assetic.layertools  (layertools.py)
    Tools to assist with using arcgis integration with assetic
"""
from __future__ import absolute_import

import arcpy
try:
    import pythonaddins
except:
    #ArcGIS Pro doesn't have this library
    pass
import assetic
import six
from ..config import Config
from .commontools import CommonTools
from .commontools import DummyProgressDialog

##version 1 apis - use to create spatial object in Assetic
b_use_v1 = True   #Flag indicating that v1 apis can be used (requests imported)
try:
    import requests    #use for v1 api's
    import json
except ImportError:
    b_use_v1 = False
    
class LayerTools(object):
    """
    Class to manage processes that sync Assetic search data to a local DB
    """

    def __init__(self, layerconfig=None):
        
        self.config = Config()
        if layerconfig == None:
            self._layerconfig = self.config.layerconfig
        else:
            self._layerconfig = layerconfig
        self._assetconfig = self._layerconfig.assetconfig
        self.asseticsdk = self.config.asseticsdk

        ##initialise common tools so can use messaging method
        self.commontools = CommonTools()
        #instantiate assetic.AssetTools
        self.assettools = assetic.AssetTools(self.asseticsdk.client)

        ##get logfile name to help user find it
        self.logfilename = ""
        for h in self.asseticsdk.logger.handlers:
            try:
                self.logfilename = h.baseFilename                
            except:
                pass
            
    def get_layer_config(self,lyr,purpose):
        """
        For the given layer get the config settings. Depending on purpose not
        all config is required, so only get relevant config
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param purpose: one of 'create','update','delete','display'
        """
        lyr_config_list = [j for i, j in enumerate(
            self._assetconfig) if j["layer"] == lyr.name]
        if len(lyr_config_list) == 0:
            if purpose not in ["delete"]:
                msg = "No configuration for layer {0}".format(lyr.name)
                self.commontools.new_message(msg)
            return None,None,None
        lyr_config = lyr_config_list[0]        

        #create a list of the fields in the layer to compare config with
        actuallayerflds = list()
        for fld in arcpy.Describe(lyr).Fields:
            actuallayerflds.append(fld.Name)

        if purpose in ["create","update"]:
        #from config file build list of arcmap fields to query
            fields = list(six.viewvalues(lyr_config["corefields"]))
            if fields == None:
                msg = "missing 'corefields' configuration for layer {0}".format(
                    lyr.name)
                self.commontools.new_message(msg)
                return None,None,None
            if "attributefields" in lyr_config:
                attfields = list(six.viewvalues(lyr_config["attributefields"]))
                if attfields != None:
                    fields = fields + attfields

            ##check fields from config are in layer
            if fields != None:
                for configfield in fields:
                    if configfield not in actuallayerflds:
                        msg = "Field [{0}] is defined in configuration but is not"\
                              " in layer {1}".format(configfield,lyr.name)
                        self.commontools.new_message(msg)
                        self.asseticsdk.logger.warning(msg)
                        return None, None, None
            ##add these special fields to get geometry and centroid        
            fields.append("SHAPE@")
            fields.append("SHAPE@XY")
        else:
            fields = None

        idfield = None           
        if purpose in ["delete","display"]:
            ##get the Assetic unique ID column in ArcMap
            assetid = None        
            if "id" in lyr_config["corefields"]:
                idfield = lyr_config["corefields"]["id"]
            else:
                if "asset_id" in lyr_config["corefields"]:
                    idfield = lyr_config["corefields"]["asset_id"]
                else:
                    msg = "Asset ID and/or Asset GUID field must be defined for"\
                          "layer {0}".format(lyr.name)
                    self.commontools.new_message(msg)
                    self.asseticsdk.logger.warning(msg)
                    return None, None, None

        if idfield != None and idfield not in actuallayerflds:
            msg = "Asset ID Field [{0}] is defined in configuration but is not"\
                          " in layer {1}".format(idfield,lyr.name)
            self.commontools.new_message(msg)
            self.asseticsdk.logger.warning(msg)
            return None, None, None            
            
        return lyr_config,fields,idfield
        
    def create_asset(self,lyr,query=None):
        """
        For the given layer create new assets for the selected features only if
        features have no assetic guid.
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param query: optionally apply query filter
        """
        iPass = 0
        iFail = 0
        self.asseticsdk.logger.debug("create_asset. Layer={0}".format(lyr.name))
        #get configuration for layer
        lyr_config,fields,idfield = self.get_layer_config(lyr,"create")
        if lyr_config == None:
            return

        ##create edit session
        #desc = arcpy.Describe(lyr)
        #workspace = desc.path
        #with arcpy.da.Editor(workspace) as edit:
            #edit.startEditing(False, True)
            #edit.startOperation()
            #run update cursor
        cnt = 1
        if self.commontools.is_desktop == True:
            #desktop so give user progress dialog.  Have to declare as 'with'
            ProgressTool = pythonaddins.ProgressDialog
            ##get number of records to process for used with timing dialog
            selcount = len(lyr.getSelectionSet())

        else:
            #not desktop so give use dummy progress dialog.
            ProgressTool = DummyProgressDialog()
            #consider arcpy.SetProgressor

        with ProgressTool as dialogtools:
            if self.commontools.is_desktop:
                dialog = dialogtools
                dialog.title = "Assetic Integration"
                dialog.description = "Creating Assets for layer {0}.".format(
                lyr.name)
                dialog.canCancel = False

            # Create update cursor for feature class
            with arcpy.da.UpdateCursor(lyr, fields, query) as cursor:
                for row in cursor:
                    if self.commontools.is_desktop:
                        dialog.progress = cnt/selcount*100
                    if self._new_asset(row,lyr_config,fields):
                        cursor.updateRow(row)
                        iPass = iPass + 1
                    else:
                        iFail = iFail + 1
                    cnt = cnt + 1
                      
        message = "Finished {0} Asset Creation, {1} Assets created".format(
            lyr.name,str(iPass))
        if iFail > 0:
            message = message + ", {0} assets could not be created "\
                      "(check log file {1})".format(
                str(iFail),self.logfilename)
        self.commontools.new_message(message)

    def update_assets(self,lyr):
        """
        For the given layer create update assets for the selected features only if
        features have an assetic guid.
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        """
        # Script Variables
        iPass = 0
        iFail = 0

        ##get layer configuration from xml file
        lyr_config,fields,idfield = self.get_layer_config(lyr,"update")
        if lyr_config == None:
            return

        #alias core fields for readability
        corefields = lyr_config["corefields"]

        cnt = 1        
        if self.commontools.is_desktop == True:
            #desktop so give user progress dialog.  Have to declare as 'with'
            ProgressTool = pythonaddins.ProgressDialog
            ##get number of records to process for use with timing dialog
            selcount = len(lyr.getSelectionSet())
        else:
            #not desktop so give use dummy progress dialog.
            ProgressTool = DummyProgressDialog()
        with ProgressTool as dialog:
            if self.commontools.is_desktop:
                dialog.title = "Assetic Integration"
                dialog.description = "Updating assets for layer {0}".format(
                    lyr.name)
                dialog.canCancel = False 
            # Create update cursor for feature class 
            with arcpy.da.UpdateCursor(lyr, fields) as cursor:
                for row in cursor:
                    if ("id" in corefields and \
                    row[fields.index(corefields["id"])] != None and \
                    row[fields.index(corefields["id"])].strip() != "") or\
                    ("asset_id" in corefields and \
                    row[fields.index(corefields["asset_id"])] != None and \
                    row[fields.index(corefields["asset_id"])].strip() != ""):
                        if self.commontools.is_desktop:
                            dialog.progress = cnt/selcount*100
                        ##create instance of asset object
                        asset = assetic.Assetic3IntegrationRepresentationsComplexAssetRepresentation()
                        asset.asset_category = lyr_config["asset_category"]
                        ##apply the values from arcMap to the core fields
                        for k,v in six.iteritems(corefields):
                            if k in asset.to_dict() and v in fields:
                                setattr(asset,k,row[fields.index(v)])
                        attributes = {}
                        if "attributefields" in lyr_config:
                            for k,v in six.iteritems(lyr_config["attributefields"]):
                                if k in asset.to_dict() and v in fields:
                                    attributes[k] = row[fields.index(v)]
                        asset.attributes = attributes
                        ##now execute the update
                        try:
                            response = self.assettools.update_complex_asset(asset)
                        except assetic.rest.ApiException as e:
                            msg = "Error updating asset {0} {1} Status:{2},Reason:{3} {4}".format(
                                asset.asset_id,asset.id,e.status,e.reason,e.body)
                            self.asseticsdk.logger.error(msg)
                            self.commontools.new_message("Error Updating Asset:")
                            iFail = iFail + 1
                        else:
                            iPass = iPass + 1
                        
                        ##Now update assetic with spatial data
                        ##(TODO use V2 api when available)
                        ##we will ignore failure response for the moment
                        if asset.id == None and asset.asset_id != None:
                            response = self.assettools.get_asset(asset.asset_id)
                            if response != None:
                                asset.id = response["Id"]
                        if asset.id != None:
                            geometry = row[fields.index("SHAPE@")]
                            wkt = self.get_geom_wkt(4326,geometry)
                            midpoint = row[fields.index("SHAPE@XY")]
                            midpointxy = row[fields.index("SHAPE@XY")]
                            if len(midpointxy) == 2:
                                midpt = arcpy.Point(
                                            midpointxy[0],midpointxy[1])
                            else:
                                ##try geometry midpoint instead
                                midpt = geomtry.trueCentroid
                            midpoint = arcpy.PointGeometry(midpt,
                                                geometry.spatialReference)
                            midpointwkt = self.get_geom_wkt(4326,midpoint)
                            success = self.set_asset_address_spatial(
                                        asset.id,lyr_config,
                                        midpointwkt=midpointwkt,geometrywkt=wkt)
                        #increment counter
                        cnt = cnt + 1
                           
        message = "Finished {0} Asset Update, {1} assets updated".format(
            lyr.name,str(iPass))
        if iFail > 0:
            message = "{0}, {1} assets not updated. (Check logfile {2})".format(
                message,str(iFail),self.logfilename)
        self.commontools.new_message(message,"Assetic Integration")

    def display_asset(self,lyr):
        """
        Open assetic and display the first selected feature in layer
        :param lyr: The layer find selected assets.  Not layer name,layer object
        """
        ##get layer config details
        lyr_config,fields,idfield = self.get_layer_config(lyr,"display")
        if lyr_config == None:
            return

        self.asseticsdk.logger.debug("Layer: {0}, id field: {1}".format(
            lyr.name,idfield))
        try:
            features = arcpy.da.SearchCursor(lyr,idfield)
            row = features.next()
            assetid = str(row[0])
        except Exception as ex:
            msg = "Unexpected Error Encountered, check log file"
            self.commontools.new_message(msg)            
            self.asseticsdk.logger.error(str(ex))
            return
        if assetid == None or assetid.strip() == "":
            msg = "Asset ID or Asset GUID is NULL.\nUnable to display asset"
            self.commontools.new_message(msg)
            self.asseticsdk.logger.warning(str(ex))
            return
        self.asseticsdk.logger.debug("Selected Asset to display: [{0}]".format(
            assetid))
        #Now launch Assetic
        apihelper = assetic.APIHelper(self.asseticsdk.client)
        apihelper.launch_assetic_asset(assetid)

    def _new_asset(self,row,lyr_config,fields):
        """
        Create a new asset for the given search result row
        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :returns: Boolean True if success, else False
        """
        
        ##instantiate the complete asset representation
        complete_asset_obj = assetic.AssetToolsCompleteAssetRepresentation()

        #create an instance of the complex asset object
        asset = assetic.Assetic3IntegrationRepresentationsComplexAssetRepresentation()

        ##set status (mandatory field)
        asset.status = "Active"
        
        ##set values from arcmap attribute table row from query
        asset.asset_category = lyr_config["asset_category"]

        #alias core fields for readability
        corefields = lyr_config["corefields"]
        
        ##set core field values from arcmap
        for k,v in six.iteritems(corefields):
            if k in asset.to_dict() and v in fields and \
            row[fields.index(v)] != None and \
            str(row[fields.index(v)]).strip() != "":
                setattr(asset,k,row[fields.index(v)])
        ##set core field values from defaults
        for k,v in six.iteritems(lyr_config["coredefaults"]):
            if k in asset.to_dict() and str(v).strip() != "":
                setattr(asset,k,v)

        ##Now we have core fields verify it actually needs to be created
        newasset = False
        if "id" in corefields:
            ##guid field set in ArcMap, use id as test
            if asset.id == None or asset.id.strip() == "":
               newasset = True
        else:
            ##guid not used, assume asset id is indicator
            if asset.asset_id == None or asset.asset_id.strip() == "":
               newasset = True
            else:
                ##test assetic for the asset id.  Perhaps user is not using guid
                ##and is manually assigning asset id.
                chk = self.assettools.get_asset(asset.asset_id)
                if chk == None:
                    newasset = True
        if newasset == False:
            msg = "Asset not created becuase it already has the following "\
                  "values: Asset ID={0},Asset GUID={1}".format(
                      asset.asset_id,asset.id)
            self.asseticsdk.logger.debug(msg)
            return False

        #It's a new asset...
        attributes = {}
        ##set attributes values from arcmap
        if "attributefields" in lyr_config:
            for k,v in six.iteritems(lyr_config["attributefields"]):
                if v in fields and row[fields.index(v)] != None and \
                str(row[fields.index(v)]).strip() != "":
                    attributes[k] = row[fields.index(v)]
        ##set attribute values from defaults
        for k,v in six.iteritems(lyr_config["attributedefaults"]):
            if str(v).strip() != "":
                attributes[k] = v
        #add the attributes to the asset and the asset to the complete object
        asset.attributes = attributes
        complete_asset_obj.asset_representation = asset

        #Create new asset
        response = self.assettools.create_complete_asset(
            complete_asset_obj)
        if response is None:
            msg = "Asset Not Created - Check log"
            self.commontools.new_message(msg)
            return False
        ##apply asset guid and/or assetid
        if "id" in corefields:
            row[fields.index(corefields["id"])] = \
                response.asset_representation.id
        if "asset_id" in corefields:
            row[fields.index(corefields["asset_id"])] = \
                response.asset_representation.asset_id
        ##Now update assetic with spatial data (TODO use V2 api when available)
        geometry = row[fields.index('SHAPE@')]
        wkt = self.get_geom_wkt(4326,geometry)
        midpointxy = row[fields.index("SHAPE@XY")]
        if len(midpointxy) == 2:
            midpt = arcpy.Point(midpointxy[0],midpointxy[1])
        else:
            ##try geometry midpoint instead
            midpt = geomtry.trueCentroid
        midpoint = arcpy.PointGeometry(midpt,geometry.spatialReference)
        midpointwkt = self.get_geom_wkt(4326,midpoint)
        success = self.set_asset_address_spatial(
                    response.asset_representation.id,lyr_config,
                    midpointwkt=midpointwkt,geometrywkt=wkt)
        return True
    
    def get_geom_wkt(self,outsrid,geometry):
        """
        Get the well known text for a geometry in 4326 projection
        :param outsrid: The projection EPSG code to export WKT as (integer)
        :param geometry: The input geometry
        :returns: wkt string of geometry in the specified projection
        """
        tosr = arcpy.SpatialReference(outsrid)
        new_geom = geometry.projectAs(tosr)
        wkt = new_geom.WKT
        return wkt

    def GetEventAssetID(self,geometryObj,oidList,layerList):
        """
        Gets the guid for an asset feature that has been deleted or moved
        https://github.com/savagemat/PythonEditCounter/blob/master/Install/PythonEditCounter_addin.py
        :param geometryObj: The feature that was deleted or moved
        :param oidList: A list of OIDs as integers
        :param layerList: Layers in the workspace
        :returns: Unique Assetic ID of the feature that was deleted/moved
        """
        assetlayers = {}
        for lyr in layerList:
            if lyr.isFeatureLayer:
                ##get layer config details
                lyr_config,fields,idfield = self.get_layer_config(
                                            lyr,"delete")                    
                if idfield != None:
                    oidField = arcpy.Describe(lyr).OIDFieldName
                    query = "{0} in {1}".format(oidField,str(oidList).replace(
                                            '[','(').replace(']',')'))
                    with arcpy.da.SearchCursor(lyr,[oidField,"SHAPE@",idfield],
                                   where_clause=query) as rows:
                        for row in rows:
                            geom = row[1]
                            if geom.JSON == geometryObj.JSON:
                                ##return the assetid and the layer it belongs to
                                return row[2],lyr
                            
        #feature is not a valid asset so return nothing
        return None,None
    
    def undo_edit(self,lyr):
        """
        Not implemented.  Works outside of edit session but not in
        need to figure out how to access
        """
        desc = arcpy.Describe(lyr)
        workspace = desc.path
        with arcpy.da.Editor(workspace) as edit:
            edit.abortOperation()

    def get_layer_asset_guid(self,assetid,lyr_config):
        """
        Get the asset guid for an asset.  Used where "id" is not in the
        configuration.  If it is then it is assumed the assetid is a guid
        :param assetid: The assetid - may be guid or friendly
        :param lyr: the layer
        :returns: guid or none
        """        
        #alias core fields object for readability
        corefields = lyr_config["corefields"]
        if "id" not in corefields:
            ##must be using asset_id (friendly).  Need to get guid
            asset = self.assettools.get_asset(assetid)
            if asset != None:
                assetid = asset["Id"]
            else:
                msg = "Asset with ID [{0}] not found in Assetic".format(
                    assetid)
                self.asseticsdk.logger.warning(msg)
                return None
        return assetid

###V1 APIs#############
    def set_asset_address_spatial(self,assetid,lyr_config,addr=None,midpointwkt=None,geometrywkt=None):
        """
        Set the address and/or spatial definition for an asset
        :param assetid: The asset GUID (TODO support friendly ID)
        :param addr: Address representation.  Optional.
        assetic.Assetic3IntegrationRepresentationsCustomAddress
        :param geometrywkt: The wkt of the spatial feature
        :returns: 0=no error, >0 = error
        """
        if addr == None and midpointwkt == None:
            msg = "Expecting address or geometry"            
            self.asseticsdk.logger.warning(msg)
            return 0
        
        if addr !=None and \
        isinstance(addr,assetic.Assetic3IntegrationRepresentationsCustomAddress)\
        == False:
            msg = "Format of address incorrect,expecting "\
                  "assetic.Assetic3IntegrationRepresentationsCustomAddress"            
            self.asseticsdk.logger.debug(msg)
            return 1
        else:
            addr = assetic.Assetic3IntegrationRepresentationsCustomAddress()

        ##get guid
        assetguid = self.get_layer_asset_guid(assetid,lyr_config)
        if assetguid == None:
            return 1

        point = midpointwkt
        linegeom = None
        polygeom = None
        ##test geometry to get type:
        if geometrywkt != None:
            geometrywkt = geometrywkt.upper()
            if "POINT" in geometrywkt:
                point = geometrywkt
            elif "LINESTRING" in geometrywkt or "CIRCULARSTRING" in geometrywkt:
                linegeom = geometrywkt
            elif "POLYGON" in geometrywkt:
                polygeom = geometrywkt

        ##prepare API session and url       
        session,env_url = self.get_session_and_baseurl()      
        url = env_url + "/api/ComplexAssetApi/{0}/Location".format(assetguid)

        #prepare payload
        data = {"ComplexAssetPhysicalLocation":
                {"ComplexAssetId":assetguid,
                "Address":{"StreetNumber":addr.street_number,
                "StreetAddress":addr.street_address,"CitySuburb":addr.city_suburb,
                "State":addr.state,"ZipPostcode":addr.zip_postcode,
                "Country":"Australia"}},
                "ComplexAssetSpatialLocation":{"ComplexAssetId":assetguid,
                "PointString":point,"LineString":linegeom,
                "PolygonString":polygeom}}
        #address ID used to determine if update or new
        if addr.id != None:
            data["ComplexAssetPhysicalLocation"]["Address"]["Id"] = addr.id
        else:
            ##check if location exists and get address id
            response = session.get(url)
            if response.status_code != 200:
                msg = "Getting address ID.  Error {0}:".format(str(response))            
                self.asseticsdk.logger.error(msg)
                return response.status_code

            rdata = response.json()
            if rdata["ComplexAssetPhysicalLocation"] != None:
                if "Id" in rdata["ComplexAssetPhysicalLocation"]["Address"]:
                    data["ComplexAssetPhysicalLocation"]["Address"]["Id"] = \
                        rdata["ComplexAssetPhysicalLocation"]["Address"]["Id"]
                ##if addr is null then get current values so as not to overwrite
                if addr == None:
                    raddr = rdata["ComplexAssetPhysicalLocation"]["Address"]
                    daddr = data["ComplexAssetPhysicalLocation"]["Address"]
                    if "StreetNumber" in raddr:
                        daddr["StreetNumber"] = rdata["StreetNumber"]
                    if "StreetAddress" in raddr:
                        daddr["StreetAddress"] = rdata["StreetAddress"]
                    if "State" in raddr:
                        daddr["State"] = rdata["State"]
                    if "Country" in raddr:
                        daddr["Country"] = rdata["Country"]
                    if "ZipPostcode" in raddr:
                        daddr["ZipPostcode"] = rdata["ZipPostcode"]
            
        # Encode the data to create a JSON payload
        payload = json.dumps(data)

        # Update location
        response = session.post(url, data=payload)

        # Check for HTTP codes other than 201 (Created)
        if response.status_code != 201:
            msg = "Error creating spatial feature in Assetic, error:{0}".format(
                str(response))
            self.asseticsdk.logger.error(msg)
            return response.status_code
        return 0

    def get_session_and_baseurl(self):
        """
        Create a Requests session and also return base url
        :returns: tuple, authenticated requests session and base url
        """
        env_url = self.asseticsdk.client.host       
        basic_auth = self.asseticsdk.conf.username,self.asseticsdk.conf.password
        session = requests.Session()
        headers = {'content-type': 'application/json'}
        session.headers.update(headers)
        session.auth = basic_auth
        return session, env_url

    def decommission_asset(self,assetid,lyr_config,comment=None):
        """
        Set the status of an asset to decommisioned
        :param assetid: The asset GUID (TODO support friendly ID)
        :param lyr_config: config details for layer
        :param comment: A comment to accompany the decommision
        :returns: 0=no error, >0 = error
        """
        ##get guid
        assetguid = self.get_layer_asset_guid(assetid,lyr_config)
        if assetguid == None:
            return 1
        
        if comment == None:
            comment = "Decommisioned via GIS"
        if b_use_v1 == False:
            msg = "Unable to decommision asset, python requests library needed"\
                  " when using v1 api"
            self.asseticsdk.logger.error(msg)
            return 1
            
        session,env_url = self.get_session_and_baseurl()
        
        # Complex Asset to be updated 
        data = {"DecommissionTriggerCode":60,"Comments":comment}

        # Encode the data to create a JSON payload
        payload = json.dumps(data)

        # Update a Complex Asset
        url = "{0}/api/ComplexAssetApi/{1}/Decommission/60".format(env_url,
                                                                   assetguid)
        try:
            response = session.put(url, data=payload)
        except Exception as ex:
            msg = "Decommision asset.  Error message {0}".format(str(ex))
            self.asseticsdk.logger.error(msg)
            return 1
        # Check for HTTP codes other than 200 (Created)
        if response.status_code != 200:
            msg = 'Response failed with error {}'.format(str(response))
            self.asseticsdk.logger.error(msg)
            return response.status_code
        else:
            return 0        
        
