from tbears.libs.scoretest.score_test_case import ScoreTestCase
from iconservice import Address, ZERO_SCORE_ADDRESS


class TestStaking(ScoreTestCase):

    def setUp(self):
        super().setUp()
        print(ZERO_SCORE_ADDRESS)
    
    def test_zero(self):
        print(ZERO_SCORE_ADDRESS)
