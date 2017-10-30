import lbppy
class Expression(lbppy.Resource):
    def structure_type(self): #returns resource identifier
        return self.values("http://scta.info/property/structureType")

    def manifestations(self):
        return self.values("http://scta.info/property/hasManifestation")

    def canonical_manifestation(self):
        return self.values("http://scta.info/property/hasCanonicalManifestation")


	#def canonical_manifestation? # returns boolean
	#	!canonical_manifestation.to_s.nil?
	#
	# translations are a subclass of manifestations for any kind of manifestation not in the original language
	# note that this currently means the manifestations methods, will not grab translation-manifestations,
	# these must be called with translations method
    def translations(self):
        return self.values("http://scta.info/property/hasTranslation")

    def canonical_translation(self):
        return self.values("http://scta.info/property/hasCanonicalTranslation")

    #def canonical_translation?
	#		!canonical_translation.to_s.nil?

	# cannonical transcriptions refers to the canonical trancription of the canonical manifestation
	#def canonical_transcription # returns single transcription as ResourceIdentifier
	#	manifestation = self.canonical_manifestation()
	#	if (manifestation != nil):
	#		return manifestation.resource.canonical_transcription
	#		end
	#	end
	#	def canonical_transcription? #returns boolean
	#		!canonical_transcription.nil?
	#	end

    def next(self): # returns resource identifier of next expression or nil
        return self.values("http://scta.info/property/next")

    def previous(self): #returns ResourceIdentifier or nil
        return self.values("http://scta.info/property/previous")

    #def order_number(self): # returns integer
		## TODO: consider changing property so that there is more symmetry here
	#	if structure_type.short_id == "structureBlock"
	#		value("http://scta.info/property/paragraphNumber").to_s.to_i
	#	else
	#			value("http://scta.info/property/totalOrderNumber").to_s.to_i
	#		end
	#	end

    #def status(self): #returns string
	#	return self.values("http://scta.info/property/status").to_s

    def top_level_expression(self): # returns resource identifier
        #TODO make sure this can handle different structure types
        return self.values("http://scta.info/property/isPartOfTopLevelExpression")

    def item_level_expression(self): # returns resource identifier
        #TODO make sure this can handle different structure types
        return self.values("http://scta.info/property/isPartOfStructureItem")

	#def level(self): # returns resource integer
		#same comment as earlier; this query does not actually return a uri,
		#but an litteral. We need to make sure the resource identifer can handle that
	#	values("http://scta.info/property/level").to_s.to_i

    def abbreviates(self): # returns array of ResourceIdentifiers
        return self.values("http://scta.info/property/abbreviates")

    def abbreviatedBy(self):
        return self.values("http://scta.info/property/abbreviatedBy")

    def references(self):
        return self.values("http://scta.info/property/references")

    def referencedBy(self):
        return self.values("http://scta.info/property/referencedBy")

    def copies(self):
        return self.values("http://scta.info/property/copies")

    def copiedBy(self):
        return self.values("http://scta.info/property/copiedBy")

    def mentions(self):
        return self.values("http://scta.info/property/mentions")

    def quotes(self):
        return self.values("http://scta.info/property/quotes")

    def quotedBy(self):
        return self.values("http://scta.info/property/quotedBy")

    def isRelatedTo(self):
        return self.values("http://scta.info/property/isRelatedTo")
