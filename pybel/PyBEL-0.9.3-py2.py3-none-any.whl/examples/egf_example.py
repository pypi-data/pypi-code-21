# -*- coding: utf-8 -*-

"""The following is an example on EGF's effect on cellular processes

.. code-block:: none

    SET Citation = {"PubMed","Clin Cancer Res 2003 Jul 9(7) 2416-25","12855613"}
    SET Evidence = "This induction was not seen either when LNCaP cells were treated with flutamide or conditioned medium were pretreated with antibody to the epidermal growth factor (EGF)"
    SET Species = 9606

    tscript(p(HGNC:AR)) increases p(HGNC:EGF)

    UNSET ALL

    SET Citation = {"PubMed","Int J Cancer 1998 Jul 3 77(1) 138-45","9639405"}
    SET Evidence = "DU-145 cells treated with 5000 U/ml of IFNgamma and IFN alpha, both reduced EGF production with IFN gamma reduction more significant."
    SET Species = 9606

    p(HGNC:IFNA1) decreases p(HGNC:EGF)
    p(HGNC:IFNG) decreases p(HGNC:EGF)

    UNSET ALL


    SET Citation = {"PubMed","DNA Cell Biol 2000 May 19(5) 253-63","10855792"}
    SET Evidence = "Although found predominantly in the cytoplasm and, less abundantly, in the nucleus, VCP can be translocated from the nucleus after stimulation with epidermal growth factor."
    SET Species = 9606

    p(HGNC:EGF) increases tloc(p(HGNC:VCP),GOCCID:0005634,GOCCID:0005737)

    UNSET ALL

    SET Citation = {"PubMed","J Clin Oncol 2003 Feb 1 21(3) 447-52","12560433"}
    SET Evidence = "Valosin-containing protein (VCP; also known as p97) has been shown to be associated with antiapoptotic function and metastasis via activation of the nuclear factor-kappaB signaling pathway."
    SET Species = 9606

    cat(p(HGNC:VCP)) increases tscript(complex(p(HGNC:NFKB1), p(HGNC:NFKB2), p(HGNC:REL), p(HGNC:RELA), p(HGNC:RELB)))
    tscript(complex(p(HGNC:NFKB1), p(HGNC:NFKB2), p(HGNC:REL), p(HGNC:RELA), p(HGNC:RELB))) decreases bp(MESHPP:Apoptosis)

    UNSET ALL
"""

from ..constants import *
from ..dsl.nodes import protein, protein_complex
from ..struct.graph import BELGraph

__all__ = [
    'egf_graph'
]

egf_graph = BELGraph(
    name='EGF Pathway',
    version='1.0.0',
    description="The downstream effects of EFG"
)

egf_graph.namespace_url.update({
    'HGNC': 'https://arty.scai.fraunhofer.de/artifactory/bel/namespace/hgnc-human-genes/hgnc-human-genes-20170725.belns',
    'CHEBI': 'https://arty.scai.fraunhofer.de/artifactory/bel/namespace/chebi/chebi-20170725.belns',
    'GOBP': 'https://arty.scai.fraunhofer.de/artifactory/bel/namespace/go-biological-process/go-biological-process-20170725.belns'
})

egf_graph.annotation_url.update({
    'Confidence': 'https://arty.scai.fraunhofer.de/artifactory/bel/annotation/confidence/confidence-1.0.0.belanno',
    'Species': 'https://arty.scai.fraunhofer.de/artifactory/bel/annotation/species-taxonomy-id/species-taxonomy-id-20170511.belanno'
})

ar = protein('HGNC', 'AR')
egf = protein('HGNC', 'AR')
ifna1 = protein('HGNC', 'IFNA1')
ifng = protein('HGNC', 'IFNG')
vcp = protein('HGNC', 'VCP')

nfkb1 = protein('HGNC', 'NFKB1')
nfkb2 = protein('HGNC', 'NFKB2')
rel = protein('HGNC', 'REL')
rela = protein('HGNC', 'RELA')
relb = protein('HGNC', 'RELB')

nfkb_complex = protein_complex([nfkb1, nfkb2, rel, rela, relb])

apoptosis = {
    FUNCTION: BIOPROCESS,
    NAMESPACE: 'GOBP',
    NAME: 'apoptotic process',
    ID: '0006915'
}

egf_graph.add_qualified_edge(
    ar,
    egf,
    relation=INCREASES,
    citation={
        CITATION_TYPE: CITATION_TYPE_PUBMED,
        CITATION_REFERENCE: '12855613'
    },
    evidence='This induction was not seen either when LNCaP cells were treated with flutamide or conditioned medium were pretreated with antibody to the epidermal growth factor (EGF)',
    annotations={'Species': '9606'},
    subject_modifier={
        MODIFIER: ACTIVITY,
        EFFECT: {
            NAMESPACE: BEL_DEFAULT_NAMESPACE,
            NAME: 'tscript'
        }
    }
)

egf_graph.add_qualified_edge(
    ifna1,
    egf,
    relation=DECREASES,
    citation={
        CITATION_TYPE: CITATION_TYPE_PUBMED,
        CITATION_REFERENCE: '9639405'
    },
    evidence='DU-145 cells treated with 5000 U/ml of IFNgamma and IFN alpha, both reduced EGF production with IFN gamma reduction more significant.',
    annotations={'Species': '9606'}
)

egf_graph.add_qualified_edge(
    ifng,
    egf,
    relation=DECREASES,
    citation={
        CITATION_TYPE: CITATION_TYPE_PUBMED,
        CITATION_REFERENCE: '9639405'
    },
    evidence='DU-145 cells treated with 5000 U/ml of IFNgamma and IFN alpha, both reduced EGF production with IFN gamma reduction more significant.',
    annotations={'Species': '9606'}
)

egf_graph.add_qualified_edge(
    egf,
    vcp,
    relation=INCREASES,
    citation={
        CITATION_TYPE: CITATION_TYPE_PUBMED,
        CITATION_REFERENCE: '10855792'
    },
    evidence='Although found predominantly in the cytoplasm and, less abundantly, in the nucleus, VCP can be translocated from the nucleus after stimulation with epidermal growth factor.',
    annotations={'Species': '9606'},
    object_modifier={
        MODIFIER: TRANSLOCATION,
        EFFECT: {
            FROM_LOC: {NAMESPACE: 'GOCC', NAME: 'nucleus', ID: '0005634'},
            TO_LOC: {NAMESPACE: 'GOCC', NAME: 'cytoplasm', ID: '0005737'},
        }
    }
)

egf_graph.add_qualified_edge(
    vcp,
    nfkb_complex,
    relation=INCREASES,
    citation={
        CITATION_TYPE: CITATION_TYPE_PUBMED,
        CITATION_REFERENCE: '12560433'
    },
    evidence="Valosin-containing protein (VCP; also known as p97) has been shown to be associated with antiapoptotic function and metastasis via activation of the nuclear factor-kappaB signaling pathway.",
    annotations={'Species': '9606'},
    subject_modifier={
        MODIFIER: ACTIVITY,
        EFFECT: {
            NAMESPACE: BEL_DEFAULT_NAMESPACE,
            NAME: 'cat'
        }
    },
    object_modifier={
        MODIFIER: ACTIVITY,
        EFFECT: {
            NAMESPACE: BEL_DEFAULT_NAMESPACE,
            NAME: 'tscript'
        }
    }
)

egf_graph.add_qualified_edge(
    nfkb_complex,
    apoptosis,
    relation=DECREASES,
    citation={
        CITATION_TYPE: CITATION_TYPE_PUBMED,
        CITATION_REFERENCE: '12560433'
    },
    evidence="Valosin-containing protein (VCP; also known as p97) has been shown to be associated with antiapoptotic function and metastasis via activation of the nuclear factor-kappaB signaling pathway.",
    annotations={'Species': '9606'},
    subject_modifier={
        MODIFIER: ACTIVITY,
        EFFECT: {
            NAMESPACE: BEL_DEFAULT_NAMESPACE,
            NAME: 'tscript'
        }
    }
)
