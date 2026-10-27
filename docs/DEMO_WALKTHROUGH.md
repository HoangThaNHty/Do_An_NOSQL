# Hướng dẫn thao tác và lời giải thích khi demo

Áp dụng bản hiện tại ngày 26/10/2026. Chưa phân thời gian. TV1 dẫn dữ liệu/CRUD, TV2 dẫn cache/khóa/lượt xem, TV3 dẫn xác thực/phiên/hiệu năng.

Đây là kịch bản để nhóm thực hành; đợt hướng dẫn này không tự tạo/sửa/xóa dữ liệu demo. Các bước thay đổi dữ liệu bên dưới chỉ tác động bài trình diễn do người thao tác tự tạo, giữ nguyên 100 bài mẫu.

## Chuẩn bị trước khi trình bày

| Cửa sổ | Thiết lập |
|---|---|
| Web cửa sổ thường | http://127.0.0.1:5000, dùng admin / 123456 |
| Web cửa sổ ẩn danh | Cùng địa chỉ 127.0.0.1; dùng reader / 123456 hoặc tài khoản vừa đăng ký |
| MongoDB Compass | Kết nối mongodb://127.0.0.1:27017 → nosql_news → articles |
| Redis Insight | Kết nối 127.0.0.1, port 6379, DB0; mật khẩu theo .env hiện tại (máy demo đang không đặt) |
| PowerShell | Thư mục clone của project; mở sẵn lệnh demo_lock.py |
| Kết quả dự phòng | docs/figures/bieu_do_hieu_nang.png và docs/PERFORMANCE_REPORT.md |

Mở /api/health: app, mongo, redis phải ok; simulated_db_latency_ms=0 khi trình bày số đo thực. Nếu app đã chạy, không khởi động thêm bản thứ hai cùng port. Nếu chưa chạy:

```powershell
cd <thu-muc-clone>
# Bat MongoDB/Redis da cai, hoac: docker compose up -d --wait
.venv\Scripts\python app.py
```

Trong Redis Insight, chọn Browser để xem key; mở >_ CLI ở góc dưới trái để gõ lệnh. Tất cả lệnh TTL/GET/HGETALL/DEL dưới đây được gõ ở Redis CLI, không phải ô Filter của Compass hoặc thanh địa chỉ web.

## 1. Giới thiệu sản phẩm — TV3

**Thao tác:** Mở trang chủ; chọn một bài có ảnh để cho thấy tiêu đề, nội dung và chuyên mục. Có thể dùng bài mẫu bất kỳ; bài cache trình diễn sẽ được tạo riêng ở bước 3.

**Nói:** “Nhóm xây dựng trang tin tức với MongoDB lưu nội dung và người dùng; Redis phụ trách bộ nhớ đệm, phiên đăng nhập và bộ đếm lượt xem. Trọng tâm là tăng tốc các lần đọc lặp lại, đồng thời giữ cache phù hợp khi nội dung được chỉnh sửa.”

Không nói nội dung bài được lưu bền vững duy nhất trong Redis.

## 2. Chứng minh dữ liệu và truy vấn — TV1

**Thao tác:** Trong Compass chọn nosql_news → articles → Documents. Filter {} rồi Find để bỏ bộ lọc cũ. Mở một document, chỉ các field title, summary, content, image, category, tags, status, author, created_at. Bộ dữ liệu gốc hiện có 100 bài; con số tăng khi thêm bài trình diễn.

Filter theo chuyên mục:

```json
{"category":"Kinh tế","status":"published"}
```

Tìm tiêu đề chứa container:

```json
{"title":{"$regex":"container","$options":"i"}}
```

Ở các tùy chọn truy vấn, đặt Sort {"created_at":-1,"_id":-1}, Limit 5; đổi Skip từ 0 sang 5 rồi Find để sang nhóm kế tiếp. Xóa Skip/Limit và Reset trước khi tìm bài demo ở bước sau.

**Nói:** “MongoDB lưu mỗi bài dưới dạng document. Nhóm có lọc theo trạng thái/chuyên mục, tìm theo từ khóa, sắp xếp và phân trang. Chỉ mục hỗ trợ các truy vấn thường dùng; không có nghĩa mọi truy vấn đều dùng chỉ mục.”

Nếu giảng viên hỏi chỉ mục, mở tab Indexes: slug unique; category + created_at; author; created_at. Không nói ứng dụng đang có MongoDB text index.

**Trên web:** gõ Container để hiện gợi ý, sau đó thử contaner hoặc cang bien.

**Nói:** “Tìm kiếm trên web có chuẩn hóa tiếng Việt, lỗi gõ nhẹ và một số nhóm chủ đề. Phần gần đúng được chấm điểm ở Python sau khi lọc dữ liệu, khác với biểu thức regex vừa thao tác trực tiếp trong Compass.”

## 3. Tạo một bài trình diễn — TV1

**Web:** Đăng nhập admin / 123456 → menu tài khoản → Quản trị → Bài viết → Thêm bài viết.

| Trường | Nội dung nhập |
|---|---|
| Tiêu đề | DEMO Redis - Hành trình container |
| Chuyên mục | Kinh tế |
| Tóm tắt | Minh họa dữ liệu gốc, cache và cập nhật nội dung. |
| Nội dung | Phiên bản 1: Container được vận chuyển từ tàu đến bãi cảng rồi chuyển tiếp về kho. Các bên cần cập nhật vị trí và lịch nhận hàng để phối hợp giao nhận. |
| Đường dẫn hình ảnh | /static/images/news_009.jpg |
| Trạng thái | Đã xuất bản |
| Thẻ | container, logistics, demo |

Bấm Lưu thay đổi. Trong bảng quản trị, bấm bút chì của đúng bài này. URL có dạng /admin/articles/edit/<ID>. Copy phần ID cuối đường dẫn vào ghi chú, gọi là ID_DEMO. **Chưa bấm con mắt hoặc mở trang đọc bài này.**

Trong Compass, tìm:

```json
{"title":"DEMO Redis - Hành trình container"}
```

**Kết quả:** Document mới xuất hiện trong MongoDB, có _id riêng. Nếu trước đó có đúng 100 bài thì hiện là 101.

**Nói:** “Thao tác thêm bài trên web ghi dữ liệu vào MongoDB thông qua controller, service và model. Nhóm dùng một bài riêng để minh họa, không sửa bộ bài mẫu.”

## 4. Cache MISS rồi HIT — TV2

Ở tất cả lệnh sau, thay <ID> bằng ID_DEMO thật, không giữ dấu < >.

**Redis Insight → CLI:**

```text
DEL article:cache:<ID>
EXISTS article:cache:<ID>
```

EXISTS phải trả 0. Đây chỉ là làm lạnh một bài; không xóa DB Redis.

**Web:** Mở tab mới http://127.0.0.1:5000/api/articles/<ID>. F12 → Network → All, bật Disable cache khi DevTools đang mở, tải lại nếu cần. Nếu đã mở endpoint trước khi chuẩn bị Network, DEL lại key rồi mới tải lần cần ghi nhận.

**Lần đầu:** JSON có source=database. Sang Redis Insight gõ:

```text
TYPE article:cache:<ID>
HGETALL article:cache:<ID>
TTL article:cache:<ID>
```

TYPE là hash, có title/content, TTL dương gần 300 giây. Trong Browser có thể lọc đúng key rồi mở xem từng field.

**Nói:** “Ban đầu Redis chưa có bài này. Ứng dụng giành khóa, đọc MongoDB, ghi nội dung vào Redis rồi đặt thời gian sống 300 giây. Đây là Cache Miss của luồng Cache-Aside.”

**Lần hai:** F5 đúng tab API. JSON source=cache.

**Nói:** “Lần sau nội dung bài được lấy từ Redis. TTL không phải thời gian đọc, mà là thời gian key còn tồn tại.”

Có thể mở /admin/cache để chỉ Hit/Miss tăng. Đặt lại thống kê chỉ xóa các counter thống kê; **không xóa cache bài**. HTML còn có phần liên quan/chuyên mục nên đừng nói toàn bộ trang không chạm MongoDB chỉ vì nội dung bài là Hit; endpoint API giúp cô lập luồng cần chứng minh.

## 5. Sửa bài và chứng minh invalidation — TV1 phối hợp TV2

1. Giữ nguyên tab API, chưa tải lại.
2. TV1 mở form sửa bài, thay “Phiên bản 1” thành “Phiên bản 2: Lịch nhận container đã được cập nhật”, rồi Lưu thay đổi. Giữ nguyên tiêu đề để dễ tìm.
3. TV2 sang Redis Insight ngay, chưa mở lại trang đọc/API:

```text
EXISTS article:cache:<ID>
```

**Kết quả phải là 0.** Compass Find lại đúng bài sẽ thấy content mới.

**Nói:** “Nhóm cập nhật MongoDB trước rồi xóa cache liên quan. Nhờ vậy lần đọc sau không tiếp tục dùng bản cũ cho đến hết TTL. Key bị mất ở đây là invalidation chủ động, không phải chờ đủ 300 giây.”

4. F5 tab API: source=database và content phiên bản 2.
5. F5 thêm lần nữa: source=cache và vẫn là phiên bản 2.

Nếu vô tình mở bài trước khi kiểm tra, key sẽ được tạo lại rất nhanh. Khi đó sửa thêm một chi tiết rồi làm lại đúng thứ tự, không kết luận invalidation bị lỗi chỉ vì thấy key đã quay lại.

## 6. INCR lượt xem — TV2

**Redis Insight:**

```text
GET article:views:<ID>
```

Chưa có key là bình thường, tương đương chưa có lượt xem được ghi. Mở http://127.0.0.1:5000/articles/<ID>, sau đó tải lại trang ba lần. GET lại key để thấy số tăng. Mỗi lần tải HTML bình thường tăng một lượt; nếu mở lần đầu rồi F5 ba lần thì thường tăng tổng cộng bốn.

**Nói:** “Nhóm dùng INCR của Redis để cộng lượt xem nguyên tử. Đây là số lượt tải trang, không phải số người xem duy nhất. GET API chi tiết chỉ đọc dữ liệu nên không tăng counter.”

Có thể quay về Compass: field views trong MongoDB vẫn 0 là thiết kế hiện tại; giá trị hiển thị và thứ hạng đọc từ Redis. Counter có TTL và sẽ mất khi hết hạn, không phải tổng vĩnh viễn. Một bài mới có vài lượt xem chưa chắc đứng đầu mục Xem nhiều nhất.

## 7. Khóa chống cùng nạp DB — TV2

Chuẩn bị Redis Insight Browser lọc lock:article:cache:demo-lock-*; script tạo key riêng rồi tự dọn.

```powershell
cd <thu-muc-clone>
.venv\Scripts\python data/demo_lock.py --workers 12 --delay-ms 1000
```

**Kết quả chính:** workers=12, loader_calls=1, database_responses=1, cache_responses=11, timeouts=0, lock_removed_afterwards=true. TTL khóa khoảng 10.000 ms lúc quan sát. Khóa chỉ tồn tại ngắn, không nhất thiết kịp chụp trong GUI; kết quả JSON là bằng chứng dự phòng.

**Nói:** “Nếu nhiều yêu cầu cùng gặp cache rỗng, không có khóa thì chúng có thể cùng đọc DB. Nhóm dùng SET NX PX: một yêu cầu giữ khóa, các yêu cầu khác chờ cache. Token và Lua bảo đảm chủ cũ không nhả khóa của chủ mới. Một giây trong script là mô phỏng công việc để dễ quan sát, không phải thời gian MongoDB thực tế.”

Nếu hỏi sâu: mặc định chờ khoảng 2 giây; quá hạn trả 503 để thử lại, không bỏ qua khóa và dồn thêm truy vấn DB. Lease 10 giây không tự gia hạn; cần phù hợp thời gian bộ nạp. Script dùng counter riêng nên số chờ trên trang quản trị chính không nhất thiết tăng bởi script này. Kiểm thử HTTP thật cùng bài đã ghi nhận 1 database + 11 cache; các request đến muộn có thể Hit ngay, không phải tất cả đều chờ.

## 8. Đăng ký, phân quyền và Session Hash — TV3

Giữ admin ở cửa sổ thường để còn quản trị. Trong cửa sổ ẩn danh mở /register, đăng ký tên mới, ví dụ demo_reader_2610, email demo_reader_2610@example.com, mật khẩu Demo123456. Nếu tên đã dùng khi tập, đổi hậu tố. Đăng ký thành công chuyển về /login; đăng nhập bằng tài khoản vừa tạo.

**Web:** Mở /profile: vai trò Độc giả. Thử nhập trực tiếp /admin/: bị chuyển về trang chủ, không vào được trang quản trị.

**Nói:** “Đăng ký công khai luôn tạo Độc giả. Quyền được kiểm tra ở máy chủ; ẩn một nút trên giao diện không đủ để bảo vệ chức năng.”

Ở **cùng cửa sổ ẩn danh đã đăng nhập**, mở /api/auth/session. Copy data.session_id, gọi là SID. Redis Insight:

```text
TYPE session:<SID>
HGETALL session:<SID>
TTL session:<SID>
```

**Kết quả:** Hash có username, user_id, role=reader, login_at…, TTL ban đầu gần 1800 giây.

**Nói:** “Trình duyệt giữ cookie chứa mã phiên. Thông tin phiên nằm trong Redis Hash, không nằm toàn bộ trong cookie và không chứa mật khẩu.”

Chờ vài giây chỉ ở Redis Insight rồi gõ TTL lại. Dừng request của chính SID đang quan sát; trang /admin/cache có polling mỗi 10 giây và sẽ gia hạn phiên của nó. Admin ở cửa sổ thường là SID khác, không gia hạn SID reader trong ẩn danh.

F5 /profile ở cửa sổ ẩn danh rồi xem TTL: trở lại gần 1800.

**Nói:** “Phiên được gia hạn khi có hoạt động. Khi ngừng hoạt động, TTL giảm; hết hạn thì phiên không còn hợp lệ.”

Bấm Đăng xuất ở cửa sổ ẩn danh. Redis Insight gõ EXISTS session:<SID> → 0; TTL → -2. Truy cập lại /profile → trang đăng nhập.

**Nói:** “Đăng xuất xóa cả session phía Redis và cookie. Người dùng không thể tiếp tục dùng phiên vừa đăng xuất để mở trang cá nhân.”

## 9. Hiệu năng — TV3

Mở docs/figures/bieu_do_hieu_nang.png và docs/figures/bang_so_sanh.md. Số đo thật đã lưu:

| Kịch bản | DB/MISS TB | Redis/HIT TB |
|---|---:|---:|
| Nội dung bài | 0,709 ms | 0,519 ms |
| Danh sách 9 bài | 2,769 ms | 0,752 ms |
| HTTP request | 12,889 ms | 8,554 ms |

**Nói:** “Nhóm đo 200 mẫu mỗi nguồn sau 10 lượt khởi động, dùng cùng dữ liệu trả về. Chuẩn bị và xóa cache nằm ngoài đồng hồ đo. Thời gian cả HTTP request gồm xử lý ứng dụng và giao tiếp, nên lớn hơn riêng thời gian đọc dữ liệu.”

Nếu hỏi p95: “Khoảng 95% mẫu nằm không vượt quá mức p95 trong lần đo này; đó không phải thời gian trung bình hay cam kết cho mọi lần chạy.”

Mở bieu_do_mo_phong.png riêng và nói rõ: “Đây là thêm 50ms mô phỏng ở đường MongoDB, không phải mạng thật.” Không nói HTTP Hit đã dưới 5ms: số thực tế trung bình hiện là 8,554ms.

Lệnh chạy lại, khi cần và chấp nhận chờ phép đo hoàn tất:

```powershell
.venv\Scripts\python data/benchmark.py --n 200 --warmup 10 --http http://127.0.0.1:5000 --rtt 50
.venv\Scripts\python data/plot_benchmark.py
```

## 10. Xóa bài trình diễn — TV1

Chỉ xóa bài DEMO Redis - Hành trình container bằng biểu tượng thùng rác trong quản trị, xác nhận hộp thoại. Compass tìm theo ID → không còn document; API đúng ID → 404; Redis EXISTS article:cache:<ID> → 0.

**Nói:** “Khi xóa bài, nhóm xóa dữ liệu gốc và vô hiệu cache liên quan, tránh đọc lại nội dung đã bị xóa.”

Không hứa key article:views:<ID> bị xóa ngay: counter hiện có TTL riêng. Không dùng sự tồn tại counter để kết luận bài hoặc cache vẫn tồn tại.

## Phần bổ sung: aggregation trên Compass

Trong articles → Aggregations, dùng Stages; + Add Stage, chọn toán tử rồi nhập phần nội dung tương ứng:

| Stage | Nội dung |
|---|---|
| $match | {"status":"published"} |
| $group | {"_id":"$category","so_bai":{"$sum":1}} |
| $sort | {"so_bai":-1} |

Bấm Run. Kết quả là số bài đã xuất bản theo chuyên mục, không sửa dữ liệu.

**Nói:** “Ngoài lấy từng document, MongoDB còn thực hiện pipeline lọc, gom nhóm và sắp xếp để tạo thống kê.” Đây là truy vấn trực tiếp trên GUI để trình bày, không khẳng định website đang có màn thống kê aggregation này.

## Phần bổ sung: import/export trên Compass

Làm trước bước xóa cuối cùng nếu muốn minh họa vòng export → xóa → import một bài:

1. Documents → Filter {"_id":ObjectId("<ID>")} → Find. Chắc chỉ có bài DEMO.
2. Export Data → Export query results → All Fields → JSON → Default Extended JSON hoặc Canonical Extended JSON; lưu một file riêng.
3. Xóa chính bài DEMO bằng web để ứng dụng chạy invalidation; không xóa bộ 100 bài.
4. Compass → Add Data → Import JSON or CSV file → chọn file JSON vừa xuất → Import.
5. Tìm lại đúng ID và mở URL chi tiết bài: dữ liệu được khôi phục. Giữ _id trong file giúp đường dẫn cũ hoạt động lại. Cuối buổi có thể xóa bài DEMO lần nữa.

**Nói:** “Đây là minh họa xuất và nhập lại một document, giữ định dạng BSON qua Extended JSON. Nó không thay thế sao lưu toàn hệ thống.”

Backup/restore của dự án là data/backup.py và data/restore.py, gồm cả MongoDB và Redis/TTL. Khi giảng viên yêu cầu demo restore toàn bộ, nên dùng DB thử đã chuẩn bị, không chạy restore --drop trực tiếp vào DB chính đang trình bày. Phần này cần diễn tập trên DB riêng trước khi đưa vào trình bày chính; tham khảo README và TESTING.md.

## Checklist khi tập

- Mỗi bước chỉ ra được: đang thao tác ở web/Compass/Insight, bằng chứng là gì, giải thích một câu.
- ID_DEMO và SID là hai mã khác nhau; key bài dùng ID bài, key session dùng SID.
- Browser của Redis Insight không tự bảo đảm đang hiển thị dữ liệu mới: Refresh hoặc gõ lại lệnh CLI.
- Không mở bài trước khi quay cảnh MISS; không tải lại sau khi sửa trước khi kiểm tra key bị xóa.
- Cùng dùng 127.0.0.1 trên web, tránh đổi sang localhost giữa các tab vì cookie thuộc host.
- Không nhầm dữ liệu mẫu 47 key với 47 phiên thật; có cả cache/counter/thống kê và có thể có thêm metadata/khóa hệ thống.

## Tài liệu công cụ đã đối chiếu

- MongoDB Compass Filter: https://www.mongodb.com/docs/compass/query/filter/
- Aggregation Builder: https://www.mongodb.com/docs/compass/create-agg-pipeline/
- Import/export và Extended JSON: https://www.mongodb.com/docs/compass/import-export/
- Redis Insight Browser và CLI: https://redis.io/docs/latest/develop/tools/insight/
- Redis TTL: https://redis.io/docs/latest/commands/ttl/
