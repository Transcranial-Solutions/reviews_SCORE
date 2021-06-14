from ..reviews import Reviews
from iconservice import Address
from tbears.libs.scoretest.score_test_case import ScoreTestCase


#class TestReviews(ScoreTestCase):
#    def setUp(self):
#        super().setUp()
#        self.score = self.get_score_instance(Reviews, self.test_account1)
#
#    def test_set_staking_score(self):
#        staking_score = "cx1000000000000000000000000000000000000000"
#        staking_score = Address.from_string(staking_score)
#        self.score.set_staking_score(staking_score)
#
#        score = self.score._staking_score.get()
#
#        self.assertEqual(staking_score, score)
#
#    def test_submit_review(self):
#        guid = 10
#        msg_hash = "fffffff"
#        expiration = 1
#        self.set_msg(self.test_account1, 30)
#        self.score.submit_review(guid=guid, hash=msg_hash, expiration=expiration)
#
#        print("unittest: ", self.score.db)
#        res = self.score.get_review(guid)
#        self.assertEqual(res["guid"], guid)
#        self.assertEqual(res["hash"], msg_hash)
#        self.assertEqual(res["expiration"], expiration)
