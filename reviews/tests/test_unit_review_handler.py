#from iconservice import Address, VarDB
#from ..reviews import Reviews
#from ..review_handler import ReviewHandler, _Review
#from tbears.libs.scoretest.score_test_case import ScoreTestCase
#
#SENDER = "hxaea72c7d11c1e41c51d2110379b71023c5fa6d19"
#VALUE = 40


#class TestReviewHandler(ScoreTestCase):
#    def setUp(self):
#        super().setUp()
#        self.score = self.get_score_instance(Reviews, self.test_account1)
#        self.set_msg(Address.from_string(SENDER), VALUE)
#
#    def test_create_review(self):
#        review_handler = self.score._review_handler
#        prev_count = review_handler.get_review_count()
#        review_handler.create_review(1, "hash1", 100, self.score.msg.sender, self.score.msg.value)
#        review = review_handler.get_review(1)
#        
#        self.assertEqual(review.guid, 1)
#        self.assertEqual(review.hash, "hash1")
#        self.assertEqual(review.reviewer, self.score.msg.sender)
#        self.assertEqual(review.stake, self.score.msg.value)
#        self.assertEqual(review.submission, self.score.now())
#        self.assertEqual(review.expiration, 100)
#        self.assertEqual(review_handler.get_review_count(), prev_count + 1)
#
#    def test_remove_review(self):
#        review_handler = self.score._review_handler
#        review_handler.create_review(1, "hash1", 100, self.score.msg.sender, self.score.msg.value)
#        prev_count = review_handler.get_review_count()
#        review = review_handler.get_review(1)
#        review.remove()
#        
#        self.assertFalse(review.guid)
#        self.assertFalse(review.hash)
#        self.assertFalse(review.reviewer)
#        self.assertFalse(review.stake)
#        self.assertFalse(review.submission)
#        self.assertFalse(review.expiration)
#        self.assertEqual(review_handler.get_review_count(), prev_count - 1)
#
#    def test_get_review(self):
#        pass
#
#    def test_get_reviews(self):
#        review_handler = self.score._review_handler
#        review_handler.create_review(1, "hash1", 100, self.score.msg.sender, self.score.msg.value)
#        review_handler.create_review(2, "hash2", 200, self.score.msg.sender, self.score.msg.value)
#        reviews = review_handler.get_reviews([1,2])
#        review_1 = reviews[0]
#        review_2 = reviews[1]
#
#        # Reviewlist length.
#        self.assertEqual(len(reviews), 2)
#
#        # Review_1.
#        self.assertEqual(review_1.guid, 1)
#        self.assertEqual(review_1.hash, "hash1")
#        self.assertEqual(review_1.reviewer, self.score.msg.sender)
#        self.assertEqual(review_1.stake, self.score.msg.value)
#        self.assertEqual(review_1.submission, self.score.now())
#        self.assertEqual(review_1.expiration, 100)
#
#        # Review_2.
#        self.assertEqual(review_2.guid, 2)
#        self.assertEqual(review_2.hash, "hash2")
#        self.assertEqual(review_2.reviewer, self.score.msg.sender)
#        self.assertEqual(review_2.stake, self.score.msg.value)
#        self.assertEqual(review_2.submission, self.score.now())
#        self.assertEqual(review_2.expiration, 200)  
#
#    def test_get_all_reviews(self):
#        pass
