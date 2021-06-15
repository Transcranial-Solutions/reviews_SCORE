import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestTest(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        super().setUp()

        # WARNING: ICON service emulation is not working with IISS.
        # You can stake and delegate but can't get any I-Score for reward.
        # If you want to test IISS stuff correctly, set self.icon_service and send requests to the network
        self.icon_service = None
        
        # If you want to send requests to the network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
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

        self._score_address = self._deploy_score(params = params)['scoreAddress']

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS, params: dict = None) -> dict:

        # Generates an instance of transaction for deploying SCORE.
        transaction = (
            DeployTransactionBuilder()
            .from_(self._test1.get_address()) 
            .to(to)
            .step_limit(100_000_000_000)
            .nid(3)
            .nonce(100)
            .content_type("application/zip")
            .content(gen_deploy_data_content(self.SCORE_PROJECT))
            .params(params)
            .build()
        )

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertEqual(True, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def test_score_update(self):
        # update SCORE
        tx_result = self._deploy_score(self._score_address)

        self.assertEqual(self._score_address, tx_result['scoreAddress'])
