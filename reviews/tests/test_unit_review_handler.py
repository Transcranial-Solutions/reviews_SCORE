from iconservice import Address, VarDB
from ..reviews import Reviews
from ..review_handler import ReviewHandler, _Review
from tbears.libs.scoretest.score_test_case import ScoreTestCase

SENDER = 'hxaea72c7d11c1e41c51d2110379b71023c5fa6d19'
VALUE = 40

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