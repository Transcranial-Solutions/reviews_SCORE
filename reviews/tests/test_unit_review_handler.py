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
        #self.set_msg(Address.from_string(SENDER), VALUE)
        #review_handler = self.score._review_handler
        #review_handler._guids.add(2)
        #review_handler._guids.add(3)
        #print(f'Length 1: {len(review_handler._guids)}')
        #review_handler.create_review(11, "hx98257", 7894, self.score.msg.sender, self.score.msg.value)
        #review_handler.create_review(11, "hx98257", 7894, self.score.msg.sender, self.score.msg.value)
        #print(f'Length 2: {len(review_handler._guids)}')

    def test_remove_review(self):
        pass
    
    def test_get_review(self):
        #self.test_create_review()
        #review_handler = self.score._review_handler
        #review = review_handler.get_review("11")
        #print("hej")
        #print(review.reviewer)
        pass
        

    def test_get_reviews(self):
        pass

    def test_get_all_reviews(self):
        pass