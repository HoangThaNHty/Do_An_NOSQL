import argparse
import sys
import os
import re
import importlib.metadata

def mask_uri(uri):
    """Ẩn mật khẩu trong connection URI (MongoDB, Redis)"""
    if not uri:
        return "None"
    return re.sub(r":([^:@/]+)@", r":***@", uri)

def check_offline():
    print("--- KIỂM TRA OFFLINE ---")
    status = 0
    # Kiểm tra Python version
    py_version = sys.version_info
    print(f"[INFO] Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")

    # Kiểm tra dependencies từ requirements.txt
    req_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'requirements.txt'))
    if not os.path.exists(req_path):
        print(f"[WARN] Không tìm thấy {req_path}. Bỏ qua kiểm tra package.")
        return status

    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            # Lấy tên package bằng cách cắt các ký tự phiên bản
            pkg = line.strip().split('==')[0].split('>=')[0].split('~=')[0].strip()
            if not pkg or pkg.startswith('#') or pkg.startswith('-'):
                continue
            
            try:
                version = importlib.metadata.version(pkg)
                print(f"[PASS] Package '{pkg}' đã cài đặt (v{version})")
            except importlib.metadata.PackageNotFoundError:
                print(f"[FAIL] Thiếu package: '{pkg}'. Vui lòng chạy pip install -r requirements.txt")
                status = 1
    except Exception as e:
        print(f"[FAIL] Lỗi đọc requirements: {e}")
        status = 1
        
    return status

def check_services():
    print("\n--- KIỂM TRA SERVICES ---")
    status = 0
    
    # Thử load .env an toàn mà không dính dáng đến app.py
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    except ImportError:
        pass

    # 1. MongoDB
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    print(f"[INFO] Kiểm tra MongoDB tại: {mask_uri(mongo_uri)}")
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, OperationFailure
        
        # Ping nhanh với timeout 2 giây
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("[PASS] Ping MongoDB thành công.")
        client.close()
    except ImportError:
        print("[FAIL] Thiếu package 'pymongo'.")
        status = 1
    except OperationFailure:
        print("[FAIL] MongoDB: Lỗi xác thực (Sai credentials).")
        status = 1
    except ConnectionFailure:
        print("[FAIL] MongoDB: Timeout, mất kết nối hoặc host không tồn tại.")
        status = 1
    except Exception as e:
        print(f"[FAIL] Lỗi không xác định MongoDB: {e}")
        status = 1

    # 2. Redis
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    print(f"[INFO] Kiểm tra Redis tại: {mask_uri(redis_url)}")
    try:
        import redis
        
        r_client = redis.Redis.from_url(redis_url, socket_timeout=2, socket_connect_timeout=2)
        r_client.ping()
        print("[PASS] Ping Redis thành công.")
        r_client.close()
    except ImportError:
        print("[FAIL] Thiếu package 'redis'.")
        status = 1
    except redis.exceptions.AuthenticationError:
        print("[FAIL] Redis: Lỗi xác thực mật khẩu.")
        status = 1
    except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
        print("[FAIL] Redis: Timeout hoặc máy chủ chưa bật.")
        status = 1
    except Exception as e:
        print(f"[FAIL] Lỗi không xác định Redis: {e}")
        status = 1

    return status

def main():
    parser = argparse.ArgumentParser(description="Công cụ kiểm tra môi trường chạy dự án")
    parser.add_argument("--offline", action="store_true", help="Chỉ kiểm tra Python và package từ requirements.txt")
    parser.add_argument("--services", action="store_true", help="Kiểm tra cấu hình và ping DB (MongoDB, Redis)")
    args = parser.parse_args()

    if not args.offline and not args.services:
        print("[WARN] Bạn phải chỉ định --offline hoặc --services.")
        parser.print_help()
        sys.exit(1)

    final_code = 0
    if args.offline:
        if check_offline() != 0:
            final_code = 1
            
    if args.services:
        if check_services() != 0:
            final_code = 1

    if final_code == 0:
        print("\n[PASS] Môi trường đạt chuẩn!")
        sys.exit(0)
    else:
        print("\n[FAIL] Môi trường có lỗi. Vui lòng xem log phía trên.")
        sys.exit(1)

# Import module không tự chạy kiểm tra (thoả mãn điều kiện)
if __name__ == "__main__":
    main()