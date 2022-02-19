# -*- coding: utf-8 -*-

{
    'name': "Pretty community",
    'category': "Design",
    'version': "15.0.0.0.1",
    'installable': True,
    'sequence': 1,

    'license': "LGPL-3",
    'author': "MrFaBemol",
    'website': "http://www.odoo.com",

    'depends': ['web'],
    "assets": {
        "web.assets_backend": [
            "pretty_community/static/src/css/common.css",
        ],
    },

    'data': [],

    # 'qweb': [],
}
