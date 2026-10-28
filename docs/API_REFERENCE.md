# API REFERENCE - DIEM TIN

Tai lieu duoc sinh tu source Python bang AST.

**Pham vi:** Chi cac route bat dau bang `/api/`.

**Luu y:** Day la danh sach route, khong phai dac ta OpenAPI day du.

**Tong so method-route:** 20

| Method | Path | Endpoint | Mo ta | Nguon |
|---|---|---|---|---|
| GET | /api/articles | article_bp.api_list_articles | GET /api/articles?page=&per_page=&category=&q=&sort= | controllers/article_controller.py:124 |
| POST | /api/articles | article_bp.api_create_article | POST /api/articles - them bài viết moi vao MongoDB. [Decorator: admin_api_required] | controllers/article_controller.py:186 |
| DELETE | /api/articles/<article_id> | article_bp.api_delete_article | DELETE /api/articles/<id> - xoa bài viết + xoa cache lien quan. [Decorator: admin_api_required] | controllers/article_controller.py:219 |
| GET | /api/articles/<article_id> | article_bp.api_get_article | GET /api/articles/<id> - doc qua Cache-Aside, kem chi danh nguon du lieu. | controllers/article_controller.py:175 |
| PUT | /api/articles/<article_id> | article_bp.api_update_article | PUT /api/articles/<id> - sua bài viết. Sau khi sua DB goc -> service tu dong XOA CACHE (Cache Invalidation). [Decorator: admin_api_required] | controllers/article_controller.py:204 |
| GET | /api/articles/search | article_bp.api_search_articles | GET /api/articles/search?q=&category=&sort= (truy van nang cao) | controllers/article_controller.py:145 |
| GET | /api/articles/suggestions | article_bp.api_suggestions | Goi y tim kiem | controllers/article_controller.py:160 |
| POST | /api/auth/login | auth_bp.api_login | POST /api/auth/login - tra ve session_id de client tu luu cookie. | controllers/auth_controller.py:149 |
| POST | /api/auth/logout | auth_bp.api_logout | POST /api/auth/logout - xoa session tren Redis. | controllers/auth_controller.py:202 |
| POST | /api/auth/register | auth_bp.api_register | POST /api/auth/register | controllers/auth_controller.py:133 |
| GET | /api/auth/session | auth_bp.api_session | GET /api/auth/session - kiem tra phien hien tai (doc Hash tren Redis). | controllers/auth_controller.py:185 |
| POST | /api/cache/invalidate/<article_id> | cache_bp.invalidate | Xoa cache cua 1 bài viết (dung cho buoc demo 'Lượt trượt bộ nhớ đệm' lan dau). [Decorator: admin_api_required] | controllers/cache_controller.py:98 |
| GET | /api/cache/keys | cache_bp.keys | Danh sach key dang co tren Redis + TTL cua tung key. [Decorator: admin_api_required] | controllers/cache_controller.py:71 |
| POST | /api/cache/reset | cache_bp.reset | Dat lai bo dem Hit/Miss (dung khi bat dau buoi demo). [Decorator: admin_api_required] | controllers/cache_controller.py:90 |
| GET | /api/cache/sessions | cache_bp.sessions | Danh sach phien dang nhap (Hash tren Redis) kem TTL con lai. [Decorator: admin_api_required] | controllers/cache_controller.py:56 |
| GET | /api/cache/stats | cache_bp.stats | Thong ke Lượt trúng bộ nhớ đệm / Miss + so key dang luu tren Redis. [Decorator: admin_api_required] | controllers/cache_controller.py:28 |
| GET | /api/health | health | Kiem tra ket noi MongoDB + Redis (dung de kiem thu nhanh). | app.py:133 |
| GET | /api/saved | saved_bp.api_list | Danh sach bai viet da luu [Decorator: login_required] | controllers/saved_controller.py:22 |
| DELETE | /api/saved/<article_id> | saved_bp.api_change | Quan ly bai viet da luu [Decorator: login_required] | controllers/saved_controller.py:30 |
| PUT | /api/saved/<article_id> | saved_bp.api_change | Quan ly bai viet da luu [Decorator: login_required] | controllers/saved_controller.py:30 |

## Gioi han

- Khong thuc thi handler.
- Khong ket noi MongoDB hoac Redis.
- Quyen truy cap chi duoc ghi khi phat hien decorator trong source.
- Khong suy doan request/response schema.
- Route khai bao dong co the khong duoc phat hien bang phan tich tinh.
