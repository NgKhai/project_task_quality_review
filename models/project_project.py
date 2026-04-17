from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    quality_inspector_id = fields.Many2one(
        'res.users',
        string='Quality Inspector',
        help='This user will be auto-assigned to tasks when they reach the Ready for Review stage.',
    )
