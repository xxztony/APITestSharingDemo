from app.clients.order_client import call_order


def test_create_valid_order_should_return_accepted(record_case):
    payload = {"accountId": "ACC001", "product": "LME-CA", "side": "BUY", "quantity": 10, "price": 9125.5}
    call = call_order("POST", "/orders", payload)
    body = call["response_payload"]
    record_case(
        case_id="REST-001",
        name="Create valid order should return ACCEPTED",
        protocol="REST",
        service="order-service",
        endpoint="/orders",
        method="POST",
        expected_result="HTTP 200 and status ACCEPTED",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == 200
    assert body["status"] == "ACCEPTED"


def test_create_order_with_negative_quantity_should_return_validation_error(record_case):
    payload = {"accountId": "ACC001", "product": "LME-CA", "side": "BUY", "quantity": -1, "price": 9125.5}
    call = call_order("POST", "/orders", payload)
    record_case(
        case_id="REST-002",
        name="Create order with negative quantity should return validation error",
        protocol="REST",
        service="order-service",
        endpoint="/orders",
        method="POST",
        expected_result="HTTP 422 validation error",
        actual_result=str(call["response_payload"]),
        **call,
    )
    assert call["response_status"] == 422


def test_create_order_over_quantity_limit_should_return_rejected(record_case):
    payload = {"accountId": "ACC001", "product": "LME-ZN", "side": "BUY", "quantity": 15001, "price": 2741.8}
    call = call_order("POST", "/orders", payload)
    body = call["response_payload"]
    record_case(
        case_id="REST-003",
        name="Create order with quantity greater than 10000 should return REJECTED",
        protocol="REST",
        service="order-service",
        endpoint="/orders",
        method="POST",
        expected_result="HTTP 200 and status REJECTED",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == 200
    assert body["status"] == "REJECTED"
    assert body["rejectReason"] == "Quantity exceeds limit"


def test_get_existing_order_should_return_order_detail(record_case):
    payload = {"accountId": "ACC002", "product": "LME-AL", "side": "SELL", "quantity": 5, "price": 2382.2}
    created = call_order("POST", "/orders", payload)["response_payload"]
    call = call_order("GET", f"/orders/{created['orderId']}")
    body = call["response_payload"]
    record_case(
        case_id="REST-004",
        name="Get existing order should return order detail",
        protocol="REST",
        service="order-service",
        endpoint="/orders/{order_id}",
        method="GET",
        expected_result="HTTP 200 and matching orderId",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == 200
    assert body["orderId"] == created["orderId"]


def test_cancel_accepted_order_should_return_cancelled(record_case):
    payload = {"accountId": "ACC001", "product": "LME-NI", "side": "BUY", "quantity": 2, "price": 18542.4}
    created = call_order("POST", "/orders", payload)["response_payload"]
    call = call_order("PATCH", f"/orders/{created['orderId']}/cancel")
    body = call["response_payload"]
    call["request_payload"] = {"createdOrder": created, "cancelOrderId": created["orderId"]}
    record_case(
        case_id="REST-005",
        name="Cancel accepted order should return CANCELLED",
        protocol="REST",
        service="order-service",
        endpoint="/orders/{order_id}/cancel",
        method="PATCH",
        expected_result="HTTP 200 and status CANCELLED",
        actual_result=str(body),
        **call,
    )
    assert call["response_status"] == 200
    assert body["status"] == "CANCELLED"


def test_cancel_non_existing_order_should_return_error(record_case):
    call = call_order("PATCH", "/orders/ORD-NOT-FOUND/cancel")
    record_case(
        case_id="REST-006",
        name="Cancel non-existing order should return error",
        protocol="REST",
        service="order-service",
        endpoint="/orders/{order_id}/cancel",
        method="PATCH",
        expected_result="HTTP 404 ORDER_NOT_FOUND",
        actual_result=str(call["response_payload"]),
        **call,
    )
    assert call["response_status"] == 404
