from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx


class DistributionReqRewriter(SimpleReqRewriter):
    rules = [
        (rgx('/distribution/(\d+)/raw(/.*)?'),
         dict(rql=r'Any X WHERE X eid \1', vid='download')),
    ]
