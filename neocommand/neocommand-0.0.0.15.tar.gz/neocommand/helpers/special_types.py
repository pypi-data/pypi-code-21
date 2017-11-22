from mhelper import MAnnotation, MAnnotationArgs, MAnnotationFactory


class MAnnotationWithLabel( MAnnotation ):
    def __init__( self, args: MAnnotationArgs ):
        super().__init__( args )


TNodeUid = MAnnotationFactory( "TNodeUid", annotation_type = MAnnotationWithLabel )[str]
TEntityProperty = MAnnotationFactory( "TEntityProperty", annotation_type = MAnnotationWithLabel )[str]
TNodeProperty = MAnnotationFactory( "TNodeProperty", annotation_type = MAnnotationWithLabel )[str]
TEdgeProperty = MAnnotationFactory( "TEdgeProperty", annotation_type = MAnnotationWithLabel )[str]
TEntityLabel = MAnnotationFactory( "TEntityLabel" )[str]
TNodeLabel = MAnnotationFactory( "TNodeLabel" )[str]
TEdgeLabel = MAnnotationFactory( "TEdgeLabel" )[str]
TEndpointName = MAnnotationFactory( "TEndpointName" )[str]
