# -*- coding: utf-8 -*-

# Denifições do novo template
LAYOUT_BASE = {
    "conteudo": {
        "linhas": [
            ["banner-vitrine", "box-newsletter"],
            ["banner-mini", "banner-mini", "banner-mini"],
            ["banner-tarja"],
            ["listagem-marca"],
            ["listagem-produto"]
        ],
        "nested": True
    },
    "menu": True,
    "menu_lateral_expandido": True,
    "cabecalho": {
        "disposicao": "logo-na-esquerda"
    },
    "fullbanner": {
        "sidebar": "box-produto-destaque"
    },
    "secundaria": {
        "linhas": [
            ["box-fale-conosco", "box-descricao-loja"]
        ]
    },
    "coluna": {
        "posicao": "esquerda",
        "linhas": [
            ["menu-categoria-vertical"],
            ["box-produto-mais-vendido"]
        ]
    }
}

DISPOSICOES_LAYOUT = {
    '001': {
        'banner': {
            'linhas': [
                ['banner-full'],
                ['banner-mini', 'banner-mini', 'banner-mini']
            ]
        },
        'conteudo': {
            'linhas': [
                ['listagem-produto']
            ]
        }
    },
    '002': {
        'banner': {
            'linhas': [
                ['banner-full'],
                ['banner-tarja']
            ]
        },
        'conteudo': {
            'linhas': [
                ['banner-vitrine', 'box-newsletter'],
                ['listagem-produto']
            ]
        }
    },
    '003': {
        'banner': {
            'linhas': [
                ['banner-full'],
                ['banner-tarja']
            ]
        },
        'conteudo': {
            'linhas': [
                ['banner-mini', 'banner-mini', 'banner-mini'],
                ['listagem-produto']
            ]
        }
    },
    # segunda
    '004': {
        'banner': {
            'linhas': [
                ['banner-full', 'box-produto-mais-vendido'],
                ['banner-mini', 'banner-mini', 'banner-mini']
            ]
        },
        'conteudo': {
            'linhas': [
                ['listagem-produto']
            ]
        }
    },
    '005': {
        'banner': {
            'linhas': [
                ['banner-full', 'box-produto-mais-vendido'],
                ['banner-tarja']
            ]
        },
        'conteudo': {
            'linhas': [
                ['banner-vitrine', 'box-newsletter'],
                ['listagem-produto']
            ]
        }
    },
    '006': {
        'banner': {
            'linhas': [
                ['banner-full', 'box-produto-mais-vendido'],
                ['banner-tarja']
            ]
        },
        'conteudo': {
            'linhas': [
                ['banner-mini', 'banner-mini', 'banner-mini'],
                ['listagem-produto']
            ]
        }
    },
    # terceira
    '007': {
        'banner': {
            'linhas': [
                ['banner-full']
            ]
        },
        'conteudo': {
            'linhas': [
                ['listagem-produto']
            ]
        }
    },
    '008': {
        'banner': {
            'linhas': [
                ['banner-full', 'box-produto-mais-vendido']
            ]
        },
        'conteudo': {
            'linhas': [
                ['listagem-produto']
            ]
        }
    },
    '009': {
        'banner': {
            'linhas': [
                ['banner-full', 'box-produto-mais-vendido'],
                ['banner-tarja']
            ]
        },
        'conteudo': {
            'linhas': [
                ['listagem-produto']
            ]
        }
    },
    # quarta
    '010': {
        'banner': {},
        'conteudo': {
            'linhas': [
                ['banner-vitrine'],
                ['banner-mini', 'banner-mini', 'banner-mini'],
                ['listagem-produto'],
            ]
        }
    },
    '011': {
        'banner': {},
        'conteudo': {
            'linhas': [
                ['banner-vitrine', 'box-newsletter'],
                ['banner-mini', 'banner-mini', 'banner-mini'],
                ['listagem-produto'],
            ]
        }
    },
    '012': {
        'banner': {},
        'conteudo': {
            'linhas': [
                ['banner-vitrine'],
                ['banner-tarja'],
                ['listagem-produto'],
            ]
        }
    }
}

LINHAS_PADRAO_COLUNA = [
    ["menu-categoria-vertical"],
    ["box-produto-mais-vendido"]
]

COMPONENTES_CONFIGURACOES = {
    "banner-vitrine": {
        "minimo": 8,
        "nome": "Banner vitrine",
        "nested": 8
    },
    "banner-mini": {
        "nome": "Mini banner",
        "minimo": 3,
    },
    "banner-tarja": {
        "nome": "Banner tarja",
        "minimo": 12
    },
    "banner-sidebar": {
        "nome": "Banner lateral",
        "minimo": 3
    },
    "box-produto-destaque": {
        "nome": "Produtos em Destaque",
        "minimo": 4,
        "coluna": True
    },
    "box-newsletter": {
        "nome": "Box newsletter",
        "minimo": 3,
        "coluna": True
    },
    "box-descricao-loja": {
        "nome": "Descrição Loja",
        "minimo": 3,
        "coluna": True
    },
    "listagem-marca": {
        "nome": "Listagem dinamica das marcas",
        "minimo": 3
    },
    "listagem-produto": {
        "nome": "Listagem dos Produtos",
        "minimo": 9,
        "formulario_configuracao": "ListagemProdutosForm"
    },
    "menu-categoria-vertical": {
        "nome": "Menu vertical",
        "minimo": 3,
        "coluna": True
    },
    "box-produto-mais-vendido": {
        "nome": "Produtos mais vendidos",
        "minimo": 3,
        "coluna": True
    },
    "box-fale-conosco": {
        "nome": "Box fale conosco",
        "minimo": 4,
        "coluna": True
    },
    'banner-full': {
        'nome': 'Fullbanner',
        'minimo': 9
    },
    'listagem-icone-pagamento': {
        'nome': 'Ícones de formas de pagamento',
        'minimo': 3
    },
    'listagem-icone-selo': {
        'nome': 'ícones da loja',
        'minimo': 4
    },
    'listagem-pagina': {
        'nome': 'Páginas da loja',
        'minimo': 3
    },
    'listagem-rodape-categoria': {
        'nome': 'Listagem de categorias para rodapé',
        'minimo': 3,
        'coluna': False
    },
    'texto-descricao-loja': {
        'nome': 'Texto com descrição da loja',
        'minimo': 3
    },
    'componente-morto': {
        'nome': 'Componente que só serve para preencher espaço',
        'minimo': 3,
        'coluna': False
    }

}
