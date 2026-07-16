import logging
import os

import pytest
from reportportal_client import RPLogger

from app.testing import IamApiClient, KeycloakTokenManager


logging.setLoggerClass(RPLogger)


@pytest.fixture(scope="session")
def rp_logger() -> logging.Logger:
    logger = logging.getLogger("trading_qa.iam_api")
    logger.setLevel(logging.INFO)
    return logger


@pytest.fixture
def token_manager(rp_logger: logging.Logger) -> KeycloakTokenManager:
    return KeycloakTokenManager(
        token_url=os.getenv(
            "IAM_TOKEN_URL",
            "http://localhost:8180/realms/trading-demo/protocol/openid-connect/token",
        ),
        client_id=os.getenv("IAM_TEST_CLIENT_ID", "trading-demo-tests"),
        username=os.getenv("IAM_TEST_USERNAME", "qa.user"),
        password=os.getenv("IAM_TEST_PASSWORD", "qa123456"),
        refresh_skew_seconds=int(os.getenv("IAM_REFRESH_SKEW_SECONDS", "60")),
        logger=rp_logger,
    )


@pytest.fixture
def iam_api_client(token_manager: KeycloakTokenManager, rp_logger: logging.Logger) -> IamApiClient:
    return IamApiClient(
        base_url=os.getenv("BFF_URL", "http://localhost:8000"),
        token_manager=token_manager,
        logger=rp_logger,
    )


@pytest.fixture
def record_case(request):
    def _record(**case):
        request.node.user_properties.append(("case_record", case))

    return _record
