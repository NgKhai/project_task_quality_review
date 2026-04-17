from odoo import api, fields, models
from odoo.exceptions import ValidationError


# Canonical stage name used for workflow logic (case-insensitive match)
REVIEW_STAGE_NAME = 'ready for review'
DONE_STAGE_NAME = 'done'


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_done = fields.Boolean(
        string='Quality Review Passed',
        default=False,
        copy=False,
        tracking=True,
    )
    quality_inspected_date = fields.Datetime(
        string='Quality Inspected Date',
        readonly=True,
        copy=False,
        tracking=True,
    )

    # ------------------------------------------------------------------ #
    #  Workflow helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_stage_name(self):
        """Return the lowercase name of the current stage."""
        return (self.stage_id.name or '').strip().lower()

    def action_mark_review_passed(self):
        """Button action: Inspector marks review as passed."""
        for task in self:
            task.write({
                'is_done': True,
                'quality_inspected_date': fields.Datetime.now(),
            })

    # ------------------------------------------------------------------ #
    #  Stage transition logic                                             #
    # ------------------------------------------------------------------ #

    @api.onchange('stage_id')
    def _onchange_stage_id_quality(self):
        """
        When stage changes to 'Ready for Review', auto-assign the project's
        quality inspector to the task assignees.
        """
        if self._get_stage_name() == REVIEW_STAGE_NAME:
            inspector = self.project_id.quality_inspector_id
            if inspector and inspector not in self.user_ids:
                self.user_ids = [(4, inspector.id)]

    @api.constrains('stage_id', 'is_done')
    def _check_done_requires_review(self):
        """
        Server-side guard: a task cannot be moved to 'Done' unless
        quality review has passed (is_done == True).
        """
        for task in self:
            if task._get_stage_name() == DONE_STAGE_NAME and not task.is_done:
                raise ValidationError(
                    f'Task "{task.name}" cannot be moved to Done until the '
                    'Quality Review is passed. Ask the Quality Inspector to '
                    'click "Mark Review Passed" first.'
                )

    # ------------------------------------------------------------------ #
    #  Write override (handles programmatic stage changes, drag-and-drop) #
    # ------------------------------------------------------------------ #

    def write(self, vals):
        # Capture old stage before write for comparison
        old_stages = {task.id: task.stage_id for task in self}
        res = super().write(vals)

        if 'stage_id' in vals:
            for task in self:
                new_stage_name = task._get_stage_name()

                # Auto-assign inspector when entering 'Ready for Review'
                if new_stage_name == REVIEW_STAGE_NAME:
                    inspector = task.project_id.quality_inspector_id
                    if inspector and inspector not in task.user_ids:
                        task.sudo().write({'user_ids': [(4, inspector.id)]})

        return res
