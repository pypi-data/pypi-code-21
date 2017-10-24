import lbppy
class Manifestation(lbppy.Resource):

    def transcriptions(self):
        return self.values("http://scta.info/property/hasTranscription")

    def canonical_transcription(self):
        return self.values("http://scta.info/property/hasCanonicalTranscription")
