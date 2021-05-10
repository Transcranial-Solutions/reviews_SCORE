import os
import uuid
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import (
    DeployTransactionBuilder,
    CallTransactionBuilder,
)
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))
STAKING_SCORE_INSTALL_ADDRESS = "cx1000000000000000000000000000000000000000"


class TestTest(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, ".."))

    def setUp(self):
        super().setUp()

        # WARNING: ICON service emulation is not working with IISS.
        # You can stake and delegate but can't get any I-Score for reward.
        # If you want to test IISS stuff correctly, set self.icon_service and send requests to the network
        self.icon_service = None

        # If you want to send requests to the network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE

        self._score_address = self._deploy_score()["scoreAddress"]
        self._staking_score_address = self._deploy_staking_score()["scoreAddress"]
        self._test_guid = uuid.uuid4().int

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS) -> dict:
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
            .build()
        )

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertEqual(True, tx_result["status"])
        self.assertTrue("scoreAddress" in tx_result)

        return tx_result

    def _deploy_staking_score(self, to: str = STAKING_SCORE_INSTALL_ADDRESS) -> dict:
        staking_dir = os.path.abspath(os.path.join(DIR_PATH, "../../staking"))
        transaction = (
            DeployTransactionBuilder()
            .from_(self._test1.get_address())
            .to(to)
            .step_limit(100_000_000_000)
            .nid(3)
            .nonce(100)
            .content_type("application/zip")
            .content(gen_deploy_data_content(staking_dir))
            .build()
        )

        signed_transaction = SignedTransaction(transaction, self._test1)

        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertEqual(True, tx_result["status"])
        self.assertTrue("scoreAddress" in tx_result)

        return tx_result

    def test_score_update(self):
        # update SCORE
        tx_result = self._deploy_score(self._score_address)

        self.assertEqual(self._score_address, tx_result["scoreAddress"])

        tx_result = self._deploy_staking_score(self._staking_score_address)

        self.assertEqual(self._staking_score_address, tx_result["scoreAddress"])

    def test_set_staking_score(self):
        call = (
            CallTransactionBuilder()
            .from_(self._test1.get_address())
            .to(self._score_address)
            .step_limit(100_000_000)
            .nid(3)
            .nonce(100)
            .method("set_staking_score")
            .params({"score": STAKING_SCORE_INSTALL_ADDRESS})
            .build()
        )

        signed_trans = SignedTransaction(call, self._test1)
        response = self.process_transaction(signed_trans, self.icon_service)

        self.assertEqual(True, response["status"])

    def test_submit_review(self):
        call = (
            CallTransactionBuilder()
            .from_(self._test1.get_address())
            .to(self._score_address)
            .step_limit(100_000_000)
            .value(10)
            .nid(3)
            .nonce(100)
            .method("submit_review")
            .params({"guid": self._test_guid, "hash": "testhash", "expiration": 10})
            .build()
        )

        signed_trans = SignedTransaction(call, self._test1)
        response = self.process_transaction(signed_trans, self.icon_service)

        self.assertEqual(True, response["status"])

        call = (
            CallBuilder()
            .from_(self._test1.get_address())
            .to(self._score_address)
            .method("get_review")
            .params({"guid": self._test_guid})
            .build()
        )

        response = self.process_call(call, self.icon_service)

        self.assertEqual(self._test_guid, response["guid"])

    def test_remove_review(self):
        call = (
            CallTransactionBuilder()
            .from_(self._test1.get_address())
            .to(self._score_address)
            .step_limit(100_000_000)
            .nid(3)
            .nonce(100)
            .method("remove_review")
            .params({"guid": self._test_guid})
            .build()
        )

        signed_trans = SignedTransaction(call, self._test1)
        response = self.process_transaction(signed_trans, self.icon_service)

        self.assertEqual(True, response["status"])

        call = (
            CallBuilder()
            .from_(self._test1.get_address())
            .to(self._score_address)
            .method("get_review")
            .params({"guid": self._test_guid})
            .build()
        )

        response = self.process_call(call, self.icon_service)

        self.assertEqual(0, response["guid"])
