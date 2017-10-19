import graphene
from graphene import resolve_only_args
from .types import (
    ExposureScore,
    ExposureValue,
    ExposureCondition,
    Drug,
    GenePath
)
from .data import (
    get_exposure_score,
    get_exposure_value,
    get_patients,
    get_exposure_conditions,
    get_drugs_by_condition,
    get_genes_pathways_by_disease
)

class Query (graphene.ObjectType):

    exposure_score = graphene.Field (type=ExposureScore,
                                    exposureType  = graphene.String (),
                                    startDate     = graphene.String (),
                                    endDate       = graphene.String (),
                                    exposurePoint = graphene.String (),
                                    resolver      = get_exposure_score)
    
    exposure_value = graphene.Field (type=ExposureValue,
                                    exposureType  = graphene.String (),
                                    startDate     = graphene.String (),
                                    endDate       = graphene.String (),
                                    exposurePoint = graphene.String (),
                                    resolver      = get_exposure_value)

    exposure_conditions = graphene.List (of_type=ExposureCondition,
                                        chemicals = graphene.List(graphene.String))

    drugs_by_condition = graphene.List(of_type=Drug,
                                       conditions = graphene.List(graphene.String),
                                       resolver   = get_drugs_by_condition)

    gene_paths_by_disease = graphene.List (of_type=GenePath,
                                           diseases = graphene.List(graphene.String),
                                           resolver = get_genes_pathways_by_disease)
    
    def resolve_exposure_conditions (self, args, context, info):
        return get_exposure_conditions (self, args, context, info)
    
    
Schema = graphene.Schema(query=Query)


'''

{
  exposureValue(exposureType: "pm25", 
    		startDate: "2010-01-06", 
    		endDate: "2010-01-06", 
    	        exposurePoint: "35.9131996,-79.0558445") {
    value
  }
}

{
  exposureScore(exposureType: "pm25", 
    		startDate: "2010-01-06", 
    		endDate: "2010-01-06", 
    		exposurePoint: "35.9131996,-79.0558445") {
    value
  }
}

{
  exposureConditions (chemicals: [ "D052638" ] ) {
    chemical
    gene
    pathway
    pathName
    pathID
    human
  } 
}

{
  drugsByCondition (conditions: [ "d001249" ] ) {
    genericName
  } 
}

{
  genePathsByDisease (diseases: [ "d001249" ] ) {
    uniprotGene
    keggPath
    pathName
  } 
}

'''
