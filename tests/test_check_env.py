import sys
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Nối đường dẫn để import data/check_env.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data import check_env
import pymongo.errors
import redis.exceptions

@patch("data.check_env.importlib.metadata.version")
@patch("builtins.open", new_callable=mock_open, read_data="Flask==3.0.0\npymongo\nredis\n")
@patch("os.path.exists", return_value=True)
def test_offline_success(mock_exists, mock_file, mock_version, capsys):
    """Test mock thành công cho --offline"""
    mock_version.return_value = "3.0.0"
    status = check_env.check_offline()
    captured = capsys.readouterr()
    
    assert status == 0
    assert "[PASS] Package 'Flask'" in captured.out
    assert "[PASS] Package 'pymongo'" in captured.out

@patch("data.check_env.importlib.metadata.version")
@patch("builtins.open", new_callable=mock_open, read_data="Flask\nthieu_package\n")
@patch("os.path.exists", return_value=True)
def test_offline_missing_package(mock_exists, mock_file, mock_version, capsys):
    """Test mock thông báo rõ khi thiếu package"""
    def version_side_effect(pkg_name):
        if pkg_name == "thieu_package":
            raise check_env.importlib.metadata.PackageNotFoundError
        return "3.0.0"
    mock_version.side_effect = version_side_effect
    
    status = check_env.check_offline()
    captured = capsys.readouterr()
    
    assert status == 1
    assert "[FAIL] Thiếu package: 'thieu_package'" in captured.out

@patch("data.check_env.check_services")
def test_offline_verify_no_connection(mock_services):
    """Test xác minh offline không tạo client/kết nối DB"""
    with patch("sys.argv", ["check_env.py", "--offline"]):
        with pytest.raises(SystemExit) as e:
            check_env.main()
        assert e.value.code in (0, 1)
        mock_services.assert_not_called()

@patch("pymongo.MongoClient")
@patch("redis.Redis.from_url")
def test_services_success(mock_redis, mock_mongo, capsys):
    """Test mock thành công ping services, xác minh có đóng client"""
    mock_mongo_inst = MagicMock()
    mock_mongo.return_value = mock_mongo_inst
    mock_redis_inst = MagicMock()
    mock_redis.return_value = mock_redis_inst
    
    status = check_env.check_services()
    captured = capsys.readouterr()
    
    assert status == 0
    assert "[PASS] Ping MongoDB thành công" in captured.out
    assert "[PASS] Ping Redis thành công" in captured.out
    mock_mongo_inst.close.assert_called_once()
    mock_redis_inst.close.assert_called_once()

@patch("pymongo.MongoClient")
@patch("redis.Redis.from_url")
def test_services_timeout(mock_redis, mock_mongo, capsys):
    """Test mock báo lỗi khi timeout / mất kết nối"""
    mock_mongo.side_effect = pymongo.errors.ConnectionFailure("Timeout")
    mock_redis.side_effect = redis.exceptions.TimeoutError("Timeout")
    
    status = check_env.check_services()
    captured = capsys.readouterr()
    
    assert status == 1
    assert "Timeout, mất kết nối" in captured.out
    assert "Timeout hoặc máy chủ chưa bật" in captured.out

@patch("pymongo.MongoClient")
@patch("redis.Redis.from_url")
def test_services_auth_error(mock_redis, mock_mongo, capsys):
    """Test mock báo lỗi xác thực"""
    mock_mongo.side_effect = pymongo.errors.OperationFailure("Auth failed")
    mock_redis.side_effect = redis.exceptions.AuthenticationError("Auth failed")
    
    status = check_env.check_services()
    captured = capsys.readouterr()
    
    assert status == 1
    assert "Lỗi xác thực" in captured.out

def test_mask_uri():
    """Test tiện ích che dấu credentials"""
    uri1 = "mongodb://admin:super_secret_123@localhost:27017/db"
    assert check_env.mask_uri(uri1) == "mongodb://admin:***@localhost:27017/db"
    
    uri2 = "redis://:matkhau@127.0.0.1:6379/0"
    assert check_env.mask_uri(uri2) == "redis://:***@127.0.0.1:6379/0"
    
    uri3 = "mongodb://localhost:27017/"
    assert check_env.mask_uri(uri3) == "mongodb://localhost:27017/"