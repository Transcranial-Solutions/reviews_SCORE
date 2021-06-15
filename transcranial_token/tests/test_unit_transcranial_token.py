from ..transcranial_token import TranscranialToken
from tbears.libs.scoretest.score_test_case import ScoreTestCase



class TestTranscranialToken(ScoreTestCase):

    def setUp(self):
        super().setUp()

        self.name = 'TranscranialSolutionsToken'
        self.symbol = 'TST'
        self.initial_supply = 0
        self.decimals = 18
    
        params = {
            '_name': self.name,
            '_symbol': self.symbol,
            '_decimals': self.decimals,
            '_initialSupply': self.initial_supply
        }

        self.score = self.get_score_instance(TranscranialToken, self.test_account1, on_install_params=params)
        self.set_msg(sender = self.test_account1)
    
    def test_set_admin(self):
        self.score.set_admin(self.test_account1)
        self.assertEqual(self.score._admin.get(), self.test_account1)

    def test_add_minter(self):
        self.score.set_admin(self.test_account1)
        self.score.add_minter(self.test_account1)
        print(self.score.get_minters())

    def test_mint(self):
        self.test_add_minter()
        self.set_msg(sender = self.test_account1)
        self.score.mint(self.test_account2, 10**18)
        print(self.score.balanceOf(self.test_account2))