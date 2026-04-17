from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestQualityReview(TransactionCase):

    def setUp(self):
        super().setUp()
        self.inspector = self.env['res.users'].create({
            'name': 'QA Inspector', 'login': 'qa_inspector@test.com'
        })
        self.stage_review = self.env['project.task.type'].create({'name': 'Ready for Review'})
        self.stage_done = self.env['project.task.type'].create({'name': 'Done'})
        self.stage_todo = self.env['project.task.type'].create({'name': 'To-do'})
        self.project = self.env['project.project'].create({
            'name': 'Test Project',
            'quality_inspector_id': self.inspector.id,
        })
        self.task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project.id,
            'stage_id': self.stage_todo.id,
        })

    def test_auto_assign_inspector_on_review_stage(self):
        self.task.write({'stage_id': self.stage_review.id})
        self.assertIn(self.inspector, self.task.user_ids)

    def test_block_done_without_review(self):
        with self.assertRaises(ValidationError):
            self.task.write({'stage_id': self.stage_done.id})

    def test_allow_done_after_review_passed(self):
        self.task.action_mark_review_passed()
        self.task.write({'stage_id': self.stage_done.id})  # should not raise
        self.assertTrue(self.task.is_done)
        self.assertIsNotNone(self.task.quality_inspected_date)
