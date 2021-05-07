from ..reviews import Reviews
from ..review_handler import ReviewHandler
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestReviewHandler(ScoreTestCase):
    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(Reviews, self.test_account1)

    def test_create_review(self):
        pass

    def test_remove_review(self):
        pass

    def test_get_review(self):
        pass

    def test_get_reviews(self):
        pass

    def test_get_all_reviews(self):
        pass
