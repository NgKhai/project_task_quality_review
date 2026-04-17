{
    'name': 'Project Task Quality Review',
    'version': '19.0.1.0.0',
    'summary': 'QA workflow for project tasks with quality inspector assignment',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'category': 'Project',
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'data/project_task_type_data.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
}
