import pytest
from pydantic import ValidationError
from app.auth.schemas import RegisterRequest, LoginRequest


def test_register_password_boundaries():
    valid_base = {
        "email": "officer@example.com",
        "full_name": "Test Officer",
        "role_id": "507f1f77bcf86cd799439011",
        "designation": "Director",
        "department": "MoSPI",
        "employee_id": "EMP-999",
    }

    # 8 chars (lower bound) should pass
    reg_8 = RegisterRequest(**valid_base, password="a" * 8)
    assert len(reg_8.password) == 8

    # 128 chars (upper bound) should pass
    reg_128 = RegisterRequest(**valid_base, password="a" * 128)
    assert len(reg_128.password) == 128

    # 7 chars should fail
    with pytest.raises(ValidationError) as exc_7:
        RegisterRequest(**valid_base, password="a" * 7)
    assert "password" in str(exc_7.value)

    # 129 chars should fail
    with pytest.raises(ValidationError) as exc_129:
        RegisterRequest(**valid_base, password="a" * 129)
    assert "password" in str(exc_129.value)


def test_login_password_boundaries():
    # 128 chars passes
    log_128 = LoginRequest(email="officer@example.com", password="a" * 128)
    assert len(log_128.password) == 128

    # 129 chars fails
    with pytest.raises(ValidationError) as exc_129:
        LoginRequest(email="officer@example.com", password="a" * 129)
    assert "password" in str(exc_129.value)
