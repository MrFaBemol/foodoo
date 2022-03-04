# -*- coding: utf-8 -*-

{
    'name': "Recipes Manager",    
    'category': "Tools",
    'version': "15.0.0.0.1",
    'installable': True,
    'sequence': 1,
    
    'license': "OEEL-1",
    'author': "Odoo PS",
    'website': "www.odoo.com",
    
    'depends': ['uom', 'purchase', 'stock'],
    "assets": {
        "web.assets_backend": [],
    },
    
    'data': [
        'datas/rm_recipe_tag.xml',

        'security/ir.model.access.csv',
        'security/security.xml',

        'views/res_company.xml',
        'views/product_category.xml',
        'views/product_template.xml',
        'views/product_supplierinfo.xml',

        'views/rm_recipe.xml',
        'views/rm_recipe_ingredient.xml',
        'views/rm_recipe_tag.xml',
        'views/rm_recipe_step.xml',

        'views/rm_schedule.xml',
        'views/rm_schedule_day.xml',
        'views/rm_schedule_template.xml',
        'views/rm_schedule_template_day.xml',

        'views/ir_menu_items.xml',
    ],
    
    'qweb': [],
}
