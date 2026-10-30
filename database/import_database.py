"""Nhập bộ MongoDB mẫu vào database rỗng, giữ ObjectId và ngày tháng BSON.

python database/import_database.py --database nosql_news
Không xóa hay ghi đè collection đã có dữ liệu. Redis được tạo qua thao tác web.
"""
import argparse
import sys
from pathlib import Path

from bson.json_util import loads
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import config
from models import article, user


def import_database(db):
    # Đọc và kiểm tra đủ hai file trước khi thực hiện ghi.
    documents = {name: loads((ROOT / 'database' / f'{name}.json').read_text(encoding='utf-8'))
                 for name in ('articles', 'users')}
    if len(documents['articles']) != 100 or len(documents['users']) != 2:
        raise ValueError('Bo mau phai co 100 bai viet va 2 tai khoan demo.')
    if any(db[name].count_documents({}) for name in documents):
        raise ValueError('Database dich da co du lieu articles/users. Hay chon database rong; khong ghi de.')
    article.ensure_indexes(db)
    user.ensure_indexes(db)
    for name, rows in documents.items():
        db[name].insert_many(rows)
        print(f'{name}: {db[name].count_documents({})} documents')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', default=config.MONGO_DB_NAME)
    args = parser.parse_args()
    with MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        client.admin.command('ping')
        try:
            import_database(client[args.database])
        except ValueError as exc:
            parser.exit(1, str(exc) + '\n')
    print(f'Imported MongoDB database: {args.database}')
