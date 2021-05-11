from ..staking import Staking
from ..scorelib.constants import Score
from tbears.libs.scoretest.score_test_case import ScoreTestCase
from iconservice import Address


class TestStaking(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(Staking, self.test_account1)
        self.gov_score = Address.from_string("cx0000000000000000000000000000000000000000")

    def test_increment_funds(self):
        self.register_interface_score(self.gov_score)
        #self.assert_internal_call(Score.system, "setStake")
        self.assertEqual(self.score._total_delegation.get(), 0)
        self.score._increment_funds(40)
        self.assertEqual(self.score._total_delegation.get(), 40)

        self.score._increment_funds(30)
        self.assertEqual(self.score._total_delegation.get(), 70)
