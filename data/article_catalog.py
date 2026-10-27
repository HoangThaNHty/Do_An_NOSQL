"""Bộ bài đọc mẫu biên tập bằng tiếng Việt; ảnh được duyệt theo từng chủ đề.

Đây là nội dung kiến thức phục vụ đồ án, không giả lập tin thời sự có nguồn.
Mỗi chủ đề có bốn góc khai thác và dùng ảnh minh họa đúng chủ đề.
"""

# category, image number, image description, introduction, four (title, body) pairs
TOPICS = [
    ("Công nghệ", 1, "Các tủ máy chủ trong trung tâm dữ liệu",
     "Phía sau một website là hệ thống máy chủ xử lý yêu cầu và lưu trữ dữ liệu. Những tủ thiết bị trong trung tâm dữ liệu cần được bố trí để thuận tiện vận hành, làm mát và bảo trì.", [
         ("Bên trong trung tâm dữ liệu: các tủ máy chủ hoạt động ra sao?", "Mỗi tủ có thể chứa nhiều máy chủ và thiết bị mạng. Cáp kết nối được tổ chức theo tuyến để người vận hành dễ xác định thiết bị khi kiểm tra sự cố."),
         ("Vì sao trung tâm dữ liệu cần theo dõi nhiệt độ liên tục?", "Nhiệt phát sinh khi thiết bị hoạt động cần được đưa ra khỏi tủ máy. Việc theo dõi nhiệt độ giúp phát hiện luồng gió bị cản hoặc khu vực có thiết bị hoạt động bất thường."),
         ("Sắp xếp dây mạng giúp bảo trì máy chủ dễ hơn như thế nào?", "Nhãn cáp và sơ đồ kết nối giúp giảm nhầm lẫn khi thay thiết bị. Một thay đổi nhỏ cũng nên được ghi lại để các ca trực có cùng thông tin về hệ thống."),
         ("Nguồn điện dự phòng trong phòng máy có vai trò gì?", "Khi nguồn điện chính gián đoạn, hệ thống dự phòng hỗ trợ duy trì hoạt động hoặc tắt thiết bị theo trình tự. Kế hoạch vận hành cần tính đến cả thiết bị mạng và nơi lưu trữ dữ liệu."),
     ]),
    ("Công nghệ", 2, "Mã nguồn ứng dụng hiển thị trên màn hình",
     "Một ứng dụng web được tạo nên từ nhiều phần mã nguồn phối hợp với nhau. Cách tổ chức mã và kiểm tra từng thay đổi ảnh hưởng trực tiếp đến khả năng bảo trì của nhóm phát triển.", [
         ("Tách tầng trong ứng dụng web giúp nhóm lập trình làm việc ra sao?", "Tầng giao diện nhận tương tác, tầng nghiệp vụ xử lý quy tắc và tầng dữ liệu thực hiện truy vấn. Phân chia trách nhiệm rõ giúp một thay đổi giao diện ít ảnh hưởng đến cách lưu dữ liệu."),
         ("Cache-Aside: vì sao ứng dụng đọc bộ nhớ đệm trước?", "Ứng dụng tìm dữ liệu trong bộ nhớ đệm trước khi truy vấn nơi lưu trữ gốc. Nếu chưa có, ứng dụng đọc dữ liệu gốc rồi ghi bản sao vào bộ nhớ đệm kèm thời gian hết hạn."),
         ("Sửa bài viết rồi xóa cache: cách tránh hiển thị nội dung cũ", "Sau khi cập nhật dữ liệu gốc, ứng dụng xóa bản sao đã lưu trong bộ nhớ đệm. Lần đọc kế tiếp sẽ nạp nội dung mới thay vì tiếp tục dùng dữ liệu cũ cho đến hết hạn."),
         ("Một bài kiểm thử tốt cần kiểm tra hành vi nào của website?", "Bài kiểm thử nên mô tả điều người dùng mong đợi: đăng nhập thành công, không đọc được bản nháp và thấy nội dung mới sau khi chỉnh sửa. Kiểm tra hành vi giúp phát hiện lỗi khi cấu trúc mã thay đổi."),
     ]),
    ("Công nghệ", 3, "Các dòng mã JavaScript trên màn hình",
     "JavaScript bổ sung tương tác cho trang web, từ kiểm tra biểu mẫu đến tải thêm dữ liệu. Người dùng thường chỉ thấy kết quả trên giao diện, trong khi trình duyệt phải phối hợp nhiều bước xử lý.", [
         ("JavaScript biến biểu mẫu tĩnh thành giao diện có phản hồi", "Khi người dùng gửi biểu mẫu, chương trình có thể kiểm tra trường bắt buộc và hiển thị thông báo. Máy chủ vẫn cần kiểm tra lại dữ liệu vì kiểm tra ở trình duyệt có thể bị bỏ qua."),
         ("Thông báo lỗi biểu mẫu nên giúp người dùng sửa thế nào?", "Thông báo cần chỉ ra trường bị sai và cách khắc phục. Giữ lại các giá trị hợp lệ sau khi gửi thất bại giúp người dùng không phải nhập lại toàn bộ biểu mẫu."),
         ("Tải dữ liệu bất đồng bộ và những trạng thái giao diện cần có", "Một yêu cầu tải dữ liệu có thể đang chờ, thành công hoặc thất bại. Nút thao tác và thông báo cần phản ánh đúng trạng thái, đồng thời tránh gửi lặp khi người dùng bấm nhiều lần."),
         ("Vì sao website cần thử nghiệm trên màn hình điện thoại?", "Chiều rộng nhỏ làm thanh điều hướng, bảng dữ liệu và biểu mẫu thay đổi cách bố trí. Kiểm tra cuộn ngang, kích thước nút và vị trí thông báo giúp phát hiện lỗi khó thấy trên máy tính."),
     ]),
    ("Công nghệ", 5, "Người dùng đọc nội dung trên điện thoại thông minh",
     "Điện thoại là một cách tiếp cận nội dung số quen thuộc. Một trang đọc tin cần cân bằng giữa lượng thông tin, kích thước ảnh và khả năng thao tác bằng ngón tay.", [
         ("Thiết kế trang đọc tin trên điện thoại: ưu tiên nội dung nào?", "Tiêu đề, ảnh và phần tóm tắt cần giúp người đọc quyết định có mở bài hay không. Những thành phần phụ nên được bố trí sau nội dung chính để không chiếm hết màn hình đầu tiên."),
         ("Ảnh đại diện ảnh hưởng đến trải nghiệm đọc tin trên di động", "Ảnh cần mô tả đúng chủ đề và vẫn rõ khi thu nhỏ. Cắt ảnh quá sát có thể làm mất chi tiết quan trọng, khiến người đọc hiểu sai nội dung mà ảnh muốn minh họa."),
         ("Thanh tìm kiếm trên di động cần dễ nhìn và dễ sử dụng", "Ô tìm kiếm cần có nhãn rõ ràng và nút gửi dễ chạm. Khi không có kết quả, trang nên hiển thị từ khóa đã nhập cùng gợi ý đổi cách tìm thay vì để trống nội dung."),
         ("Đọc báo trên màn hình nhỏ: vì sao khoảng cách dòng quan trọng?", "Dòng chữ quá dài hoặc quá sát làm người đọc khó theo dõi. Việc giữ cỡ chữ dễ đọc, chia đoạn hợp lý và tạo khoảng nghỉ giúp bài dài thuận tiện hơn trên điện thoại."),
     ]),
    ("Kinh tế", 6, "Không gian giao dịch đông người tại sàn chứng khoán",
     "Sàn giao dịch là nơi các lệnh mua và bán được kết nối theo quy tắc thị trường. Ảnh tư liệu cho thấy một không gian giao dịch trực tiếp, khác với trải nghiệm đặt lệnh điện tử hiện nay.", [
         ("Không gian sàn giao dịch chứng khoán qua ảnh tư liệu", "Những nhóm người tập trung quanh khu vực giao dịch cho thấy vai trò của trao đổi thông tin tại sàn. Ảnh tư liệu giúp hình dung cách tổ chức hoạt động trước khi phần lớn thao tác chuyển lên hệ thống điện tử."),
         ("Lệnh mua và lệnh bán gặp nhau trên thị trường như thế nào?", "Một giao dịch hình thành khi lệnh đáp ứng điều kiện khớp của hệ thống. Giá và lượng đặt lệnh là hai thông tin cơ bản cần phân biệt khi đọc mô tả cơ chế giao dịch."),
         ("Thanh khoản là gì khi tìm hiểu thị trường chứng khoán?", "Thanh khoản mô tả khả năng mua hoặc bán mà không làm giá thay đổi quá lớn. Khối lượng giao dịch là một dữ kiện để quan sát, nhưng không thể tự nó diễn giải mọi biến động của thị trường."),
         ("Từ sàn giao dịch trực tiếp đến bảng điện tử", "Hệ thống điện tử giúp truyền lệnh và cập nhật trạng thái giao dịch. Dù hình thức thay đổi, thị trường vẫn cần quy tắc minh bạch và cách ghi nhận giao dịch nhất quán."),
     ]),
    ("Kinh tế", 7, "Các nhà giao dịch tập trung quanh một khu vực giao dịch",
     "Thông tin lưu chuyển liên tục trong một phiên giao dịch. Đọc đúng bối cảnh của dữ liệu giúp phân biệt điều đã được ghi nhận với nhận xét hoặc dự đoán về thị trường.", [
         ("Đọc dữ liệu thị trường: phân biệt giá, khối lượng và thời điểm", "Một mức giá cần đi kèm thời điểm ghi nhận. Khi so sánh hai bảng dữ liệu, cần kiểm tra chúng có dùng cùng đơn vị, cùng khoảng thời gian và cùng loại giá hay không."),
         ("Vì sao số liệu kinh tế cần có nguồn và mốc thời gian?", "Cùng một chỉ tiêu có thể được cập nhật hoặc điều chỉnh sau khi công bố. Ghi rõ nguồn và thời điểm giúp người đọc biết dữ liệu thuộc kỳ nào và tránh so sánh các số liệu không tương thích."),
         ("Ảnh tư liệu về thị trường cần được chú thích ra sao?", "Ảnh minh họa sàn giao dịch không đồng nghĩa với hình ảnh của một phiên giao dịch đang diễn ra. Chú thích cần phân biệt ảnh tư liệu với ảnh ghi nhận một sự kiện cụ thể."),
         ("Biểu đồ thị trường có thể gây hiểu nhầm khi thiếu điều gì?", "Trục đo, đơn vị và khoảng thời gian là những thành phần cần đọc trước khi diễn giải đường giá. Việc thay đổi phạm vi trục có thể khiến cùng một biến động trông lớn hoặc nhỏ hơn."),
     ]),
    ("Kinh tế", 9, "Tàu container và các cần cẩu tại cảng biển",
     "Một chuyến hàng đường biển liên quan đến tàu, cảng, kho và vận tải trên đất liền. Container giúp tổ chức hàng hóa theo đơn vị thống nhất để chuyển tiếp giữa các phương tiện.", [
         ("Hành trình của container từ tàu biển đến kho hàng", "Sau khi dỡ khỏi tàu, container được đưa đến vị trí chờ rồi chuyển sang phương tiện tiếp theo. Thông tin lô hàng và vị trí container cần được cập nhật đồng bộ giữa các bên tham gia."),
         ("Cần cẩu cảng biển phối hợp với tàu container như thế nào?", "Kế hoạch bốc dỡ xác định thứ tự xử lý container và khu vực tập kết. Việc phối hợp thiết bị nâng với phương tiện vận chuyển giúp tránh chồng chéo trong không gian làm việc."),
         ("Vì sao lịch tàu quan trọng với chuỗi cung ứng?", "Một thay đổi lịch cập cảng có thể ảnh hưởng đến xe nhận hàng và thời gian chuẩn bị kho. Các bên cần chia sẻ trạng thái thực tế để điều chỉnh kế hoạch thay vì chỉ dựa vào lịch ban đầu."),
         ("Theo dõi vị trí container bằng dữ liệu số", "Mã container giúp liên kết các lần tiếp nhận, di chuyển và giao hàng. Dữ liệu chỉ hữu ích khi được cập nhật đúng thời điểm và có cách xử lý những bản ghi thiếu hoặc trùng."),
     ]),
    ("Kinh tế", 10, "Hệ thống cần cẩu và container trong khu vực cảng",
     "Khu vực cảng phải kết nối hoạt động bốc dỡ, lưu bãi và vận chuyển. Cách bố trí không gian ảnh hưởng đến quãng đường di chuyển và khả năng xử lý hàng hóa.", [
         ("Bãi container được tổ chức để tìm hàng nhanh hơn ra sao?", "Mỗi vị trí lưu bãi cần được nhận diện rõ trong hệ thống quản lý. Khi biết vị trí và thứ tự dự kiến lấy hàng, đơn vị khai thác có thể giảm số lần di chuyển không cần thiết."),
         ("Kết nối cảng và đường bộ trong vận tải hàng hóa", "Container rời cảng thường tiếp tục hành trình bằng xe hoặc phương tiện khác. Lịch hẹn nhận hàng giúp phối hợp tài xế, thiết bị nâng và khu vực chờ tại cổng."),
         ("Dữ liệu thời gian chờ giúp quan sát hoạt động logistics", "Thời gian chờ có thể xuất hiện ở cổng, bãi hoặc lúc bốc dỡ. Tách từng giai đoạn giúp xác định điểm nghẽn cụ thể thay vì gộp mọi nguyên nhân vào tổng thời gian giao hàng."),
         ("Chuyển đổi số trong cảng bắt đầu từ thông tin lô hàng", "Một bản ghi thống nhất về lô hàng giúp các bộ phận dùng cùng dữ liệu. Trước khi tự động hóa, cần làm rõ ai cập nhật thông tin và cách kiểm tra khi dữ liệu không khớp."),
     ]),
    ("Thể thao", 11, "Trận bóng bầu dục trên sân với khán đài đông người",
     "Bóng bầu dục có cách tổ chức đội hình và chia lượt chơi riêng. Quan sát toàn cảnh sân giúp người mới nhận ra vị trí cầu thủ và mối liên hệ giữa các tuyến.", [
         ("Làm quen với bóng bầu dục qua góc nhìn toàn sân", "Thay vì chỉ theo dõi bóng, người xem có thể quan sát cách hai đội bố trí người trước mỗi lượt chơi. Sự thay đổi vị trí giúp thể hiện ý đồ phối hợp giữa các nhóm cầu thủ."),
         ("Đội hình và khoảng trống trong một trận bóng bầu dục", "Khoảng cách giữa các cầu thủ tạo ra những hướng di chuyển khác nhau. Góc nhìn rộng cho phép người xem thấy phần chuẩn bị thường không xuất hiện trong các đoạn quay cận cảnh."),
         ("Khán đài góp phần tạo nên không khí ngày thi đấu", "Âm thanh và màu sắc từ khán đài là một phần trải nghiệm tại sân. Việc tổ chức lối đi và khu vực chỗ ngồi cần hỗ trợ người xem theo dõi trận đấu thuận tiện."),
         ("Ảnh thể thao toàn cảnh kể thêm điều gì ngoài tỷ số?", "Một khung hình rộng có thể cho thấy đội hình, điều kiện sân và mật độ khán giả. Để hiểu diễn biến cụ thể, người xem vẫn cần thông tin về thời điểm chụp và bối cảnh của trận đấu."),
     ]),
    ("Thể thao", 12, "Sân vận động bóng đá được chiếu sáng vào buổi tối",
     "Một trận đấu buổi tối phụ thuộc vào nhiều khâu chuẩn bị ngoài sân cỏ. Hệ thống chiếu sáng, lối vào và khu vực khán giả cùng tạo nên trải nghiệm xem trực tiếp.", [
         ("Ánh sáng sân vận động phục vụ trận đấu buổi tối ra sao?", "Đèn cần giúp cầu thủ quan sát sân và người xem theo dõi diễn biến. Việc bố trí ánh sáng cũng liên quan đến góc quay hình và mức độ rõ của các khu vực thi đấu."),
         ("Trước giờ bóng lăn: những phần việc quanh sân vận động", "Đơn vị tổ chức kiểm tra khu vực chỗ ngồi, biển chỉ dẫn và lối di chuyển. Các nhóm vận hành cần chia sẻ thông tin để xử lý tình huống khi lượng người đến sân tăng."),
         ("Xem bóng đá trực tiếp: lựa chọn góc nhìn trên khán đài", "Vị trí ngồi ảnh hưởng đến cách quan sát khoảng cách và đội hình. Góc cao thường cho thấy cấu trúc trận đấu, trong khi vị trí gần sân thể hiện rõ hơn những pha xử lý cá nhân."),
         ("Vì sao bản đồ chỗ ngồi giúp khán giả tìm đường tốt hơn?", "Thông tin khu vực, cửa vào và số ghế cần được trình bày nhất quán. Biển chỉ dẫn dễ đọc giúp giảm việc đi ngược luồng khi khán giả tìm vị trí trước trận."),
     ]),
    ("Thể thao", 13, "Sân bóng bầu dục ngoài trời với khán đài và núi phía xa",
     "Sân thể thao ngoài trời tạo ra trải nghiệm khác với không gian thi đấu trong nhà. Mặt sân, thời tiết và cách bố trí khán đài đều ảnh hưởng đến hoạt động tổ chức.", [
         ("Sân thể thao ngoài trời và mối liên hệ với cảnh quan", "Một sân đấu có thể trở thành điểm nhận diện của khu vực nhờ vị trí và không gian xung quanh. Góc chụp toàn cảnh giúp thấy mối quan hệ giữa sân, khán đài và địa hình."),
         ("Mặt sân được chuẩn bị trước một sự kiện thể thao thế nào?", "Đơn vị vận hành kiểm tra bề mặt và các khu vực sử dụng trong ngày thi đấu. Công việc bảo trì cần được sắp lịch để không xung đột với thời gian tập luyện hoặc tổ chức sự kiện."),
         ("Khán đài ngoài trời cần thông tin hướng dẫn rõ ràng", "Người đến sân cần xác định được khu vực ngồi, lối đi và vị trí hỗ trợ. Cách phân chia khu vực hợp lý giúp việc di chuyển thuận tiện khi nhiều người cùng đến hoặc rời sân."),
         ("Góc chụp rộng giúp đọc không gian sân đấu", "Ảnh toàn cảnh thể hiện tỷ lệ giữa khu vực thi đấu và chỗ ngồi. Khi dùng ảnh minh họa, cần giữ đúng loại hình thể thao thay vì gắn mọi ảnh sân vận động vào cùng một chủ đề."),
     ]),
    ("Thể thao", 14, "Khán đài nhiều tầng bao quanh một sân bóng bầu dục",
     "Kiến trúc sân vận động cần đáp ứng cả hoạt động thi đấu và trải nghiệm khán giả. Nhiều tầng khán đài cho phép bố trí số lượng lớn chỗ ngồi quanh sân.", [
         ("Khán đài nhiều tầng tạo góc nhìn đến sân đấu ra sao?", "Độ cao và độ nghiêng của hàng ghế ảnh hưởng đến tầm nhìn. Các vị trí cần được tổ chức để hạn chế che khuất và kết nối thuận tiện với hành lang di chuyển."),
         ("Hành lang sân vận động: không gian ít xuất hiện trên truyền hình", "Hành lang kết nối các khu chỗ ngồi với cửa vào và khu dịch vụ. Khi thiết kế trải nghiệm khán giả, đây là phần quan trọng bên cạnh hình ảnh sân đấu trên truyền hình."),
         ("Điều phối dòng người trong ngày có sự kiện thể thao", "Lượng người đến và rời sân thường tập trung trong những khoảng thời gian ngắn. Thông tin chỉ dẫn và phân công nhân sự cần phù hợp với từng giai đoạn của sự kiện."),
         ("Sân vận động nhìn từ khán đài: hiểu tỷ lệ của không gian", "Ảnh chụp từ chỗ ngồi cho thấy đường biên, khoảng cách đến sân và những hàng ghế xung quanh. Đây là tư liệu phù hợp khi giới thiệu kiến trúc và trải nghiệm xem thể thao."),
     ]),
    ("Khoa học", 16, "Ảnh thiên hà xoắn ốc với vùng trung tâm sáng",
     "Thiên hà gồm sao, khí, bụi và các thành phần khác liên kết với nhau bằng hấp dẫn. Ảnh thiên hà xoắn ốc giúp người đọc hình dung cấu trúc trên quy mô lớn của vũ trụ.", [
         ("Nhận diện cấu trúc thiên hà xoắn ốc qua ảnh thiên văn", "Vùng trung tâm sáng và những cánh tay xoắn là các đặc điểm dễ quan sát trong ảnh. Độ sáng trong ảnh còn phụ thuộc cách thu nhận và xử lý dữ liệu của thiết bị."),
         ("Vì sao bụi vũ trụ xuất hiện thành những dải tối?", "Bụi có thể che ánh sáng từ những vùng nằm phía sau theo hướng quan sát. Những dải tối vì thế cũng mang thông tin về vật chất trong thiên hà, không đơn thuần là phần ảnh bị thiếu."),
         ("Ảnh thiên văn khác ảnh chụp thông thường ở điểm nào?", "Thiết bị có thể thu ánh sáng qua nhiều bộ lọc rồi kết hợp thành ảnh. Khi đọc ảnh, chú thích về bước sóng và phương pháp xử lý giúp hiểu đúng màu sắc được thể hiện."),
         ("Quan sát vùng trung tâm sáng của một thiên hà", "Độ sáng tập trung tại một khu vực gợi ý phân bố nguồn phát sáng theo góc nhìn của người quan sát. Một ảnh đơn lẻ không đủ để xác định mọi tính chất vật lý của khu vực đó."),
     ]),
    ("Khoa học", 17, "Tinh vân có vùng khí màu đỏ giữa nền sao",
     "Những đám mây khí và bụi trong không gian có thể hiện lên với hình dạng và màu sắc đa dạng. Ảnh tinh vân là điểm bắt đầu để tìm hiểu cách các nhà thiên văn thu thập ánh sáng.", [
         ("Tinh vân là gì? Bắt đầu từ những đám mây khí trong vũ trụ", "Tên gọi tinh vân được dùng cho các vùng khí và bụi quan sát được trong không gian. Để mô tả một đối tượng cụ thể, cần thêm dữ liệu và chú thích từ nguồn quan sát."),
         ("Màu đỏ trong ảnh tinh vân đến từ đâu?", "Màu sắc có thể liên quan đến ánh sáng phát ra từ khí và cách bộ lọc ghi nhận ánh sáng đó. Người đọc cần xem phương pháp tạo ảnh trước khi coi màu trong ảnh là màu nhìn thấy bằng mắt."),
         ("Nền sao giúp làm nổi bật hình dạng của tinh vân", "Các điểm sáng trên nền ảnh tạo sự tương phản với vùng khí trải rộng. So sánh vùng sáng và vùng tối là một cách quan sát ban đầu trước khi tìm hiểu dữ liệu chuyên sâu."),
         ("Chú thích ảnh thiên văn: tên đối tượng chưa phải là tất cả", "Một chú thích hữu ích còn cho biết nguồn ảnh và kỹ thuật ghi hình. Những thông tin đó giúp phân biệt ảnh minh họa, ảnh quan sát và hình mô phỏng."),
     ]),
    ("Khoa học", 18, "Máy bay SOFIA của NASA mang thiết bị quan sát thiên văn",
     "Thiết bị quan sát thiên văn không chỉ được đặt trên mặt đất hoặc trong không gian. Máy bay nghiên cứu là một ví dụ về cách đưa thiết bị lên vị trí quan sát khác với đài thiên văn thông thường.", [
         ("SOFIA: khi một máy bay trở thành nền tảng quan sát thiên văn", "Ảnh máy bay SOFIA minh họa cho cách tích hợp thiết bị khoa học với phương tiện bay. Đây là tư liệu về một nền tảng nghiên cứu, không phải hình ảnh của tên lửa hay vệ tinh."),
         ("Vì sao vị trí đặt kính thiên văn ảnh hưởng đến quan sát?", "Ánh sáng đi qua khí quyển có thể bị hấp thụ hoặc làm thay đổi tín hiệu quan sát. Lựa chọn vị trí thiết bị là một phần của việc xác định loại dữ liệu có thể thu nhận."),
         ("Một chuyến bay nghiên cứu cần phối hợp những nhóm nào?", "Nhóm vận hành máy bay và nhóm thiết bị khoa học có trách nhiệm khác nhau. Lịch bay, mục tiêu quan sát và điều kiện thiết bị cần được phối hợp trước khi thu thập dữ liệu."),
         ("Đọc ảnh máy bay nghiên cứu để hiểu công cụ khoa học", "Hình dáng phương tiện mới chỉ là phần dễ nhìn thấy. Muốn hiểu nhiệm vụ khoa học, cần tìm thêm mô tả về thiết bị và loại tín hiệu mà thiết bị được thiết kế để đo."),
     ]),
    ("Khoa học", 19, "Vùng khí và bụi vũ trụ có nhiều màu trong ảnh thiên văn",
     "Ảnh không gian thường kết hợp dữ liệu để thể hiện cấu trúc khó nhận biết bằng một lần quan sát. Màu và độ tương phản giúp làm nổi bật các khu vực có đặc điểm khác nhau.", [
         ("Khí và bụi tạo nên những hình dạng nào trong ảnh vũ trụ?", "Các vùng phát sáng và vùng che khuất ánh sáng tạo nên đường nét trong ảnh. Hình dạng quan sát được còn phụ thuộc hướng nhìn và phạm vi bước sóng được ghi nhận."),
         ("Ảnh nhiều bước sóng mở rộng cách quan sát không gian", "Những thiết bị khác nhau có thể ghi nhận các phần khác nhau của phổ ánh sáng. Khi kết hợp dữ liệu, người tạo ảnh cần giải thích cách ánh xạ tín hiệu sang màu sắc."),
         ("Vì sao ảnh không gian cần ghi rõ nguồn dữ liệu?", "Nguồn dữ liệu giúp người đọc biết thiết bị nào đã thu nhận hình ảnh. Đây cũng là cơ sở để tìm chú thích gốc thay vì suy luận chỉ từ màu và hình dạng trong ảnh."),
         ("Từ tín hiệu đến hình ảnh: một bước trong nghiên cứu thiên văn", "Dữ liệu thu nhận cần được hiệu chỉnh và xử lý trước khi trình bày. Ảnh cuối cùng là cách biểu diễn dữ liệu, còn các kết luận nghiên cứu cần dựa trên quá trình phân tích phù hợp."),
     ]),
    ("Khoa học", 20, "Một ngôi nhà nhỏ giữa cây xanh, ảnh tư liệu về địa điểm quan sát",
     "Không gian nghiên cứu có thể bắt đầu từ những công trình nhỏ và điều kiện địa điểm phù hợp. Ảnh tư liệu về một địa điểm giúp đặt hoạt động khoa học vào bối cảnh đời sống.", [
         ("Chọn địa điểm quan sát bầu trời: vì sao môi trường xung quanh quan trọng?", "Ánh sáng nhân tạo và vật cản làm thay đổi phần bầu trời có thể quan sát. Khảo sát địa điểm cần xem xét hướng nhìn, điều kiện tiếp cận và thời gian sử dụng."),
         ("Ánh sáng đô thị và trải nghiệm ngắm sao", "Một nơi ít ánh sáng xung quanh tạo điều kiện khác với khu dân cư đông đúc. Khi so sánh trải nghiệm quan sát, cần ghi lại bối cảnh thay vì chỉ dựa vào loại thiết bị sử dụng."),
         ("Ghi chép hiện trường trong một buổi quan sát thiên văn", "Thời gian, địa điểm và điều kiện bầu trời là những thông tin cần lưu cùng quan sát. Nhật ký giúp người tham gia đối chiếu các buổi khác nhau và nhận ra giới hạn của dữ liệu."),
         ("Không gian nhỏ cũng có thể phục vụ hoạt động học khoa học", "Một khu vực có tổ chức rõ ràng giúp người học chuẩn bị thiết bị và ghi chép. Điều quan trọng là mục tiêu hoạt động phù hợp với điều kiện thực tế của địa điểm."),
     ]),
    ("Xã hội", 21, "Người và phương tiện di chuyển trên đường phố vào buổi tối",
     "Không gian đường phố thay đổi khi ngày chuyển sang tối. Ánh sáng, hoạt động cửa hàng và dòng phương tiện tạo ra những nhu cầu khác nhau cho người đi bộ.", [
         ("Quan sát đường phố ban đêm từ góc nhìn người đi bộ", "Người đi bộ cần nhận diện vỉa hè, vị trí sang đường và các chướng ngại. Ảnh đường phố buổi tối gợi mở cách không gian công cộng được sử dụng ngoài giờ làm việc."),
         ("Ánh sáng đô thị giúp người đi đường định hướng thế nào?", "Biển chỉ dẫn và mặt đường cần đủ rõ để người sử dụng nhận biết không gian. Nguồn sáng từ cửa hàng không thay thế hoàn toàn cho cách tổ chức chiếu sáng đường phố."),
         ("Vỉa hè kết nối cửa hàng với đời sống khu phố", "Một đoạn vỉa hè có thể phục vụ cả việc di chuyển và tiếp cận dịch vụ. Quan sát cách sử dụng thực tế giúp nhận diện những vị trí dễ xảy ra xung đột giữa các hoạt động."),
         ("Ảnh phố đêm kể câu chuyện về nhịp sống đô thị", "Trong cùng một khung hình có thể xuất hiện người đi bộ, phương tiện và hoạt động kinh doanh. Chú thích cần mô tả đúng điều nhìn thấy thay vì suy rộng thành số liệu về cả thành phố."),
     ]),
    ("Xã hội", 22, "Người dân đi bộ trên tuyến phố có hàng cây",
     "Một tuyến phố có nhiều người đi bộ là không gian gặp gỡ và sử dụng dịch vụ. Cây xanh, chỗ nghỉ và cách phân chia lối đi ảnh hưởng đến trải nghiệm ở lại khu vực này.", [
         ("Phố đi bộ: không gian gặp gỡ trong lòng đô thị", "Người dân có thể đến để đi dạo, trò chuyện hoặc tham gia hoạt động cộng đồng. Quan sát nhiều thời điểm giúp hiểu cách không gian thay đổi theo nhóm người sử dụng."),
         ("Bóng cây tạo khoảng nghỉ cho người đi bộ", "Cây xanh góp phần tạo bóng mát và điểm nhận diện dọc tuyến phố. Việc bố trí cần cân nhắc khoảng trống đi lại và khả năng tiếp cận các công trình hai bên."),
         ("Biển chỉ dẫn trong không gian công cộng cần dễ hiểu", "Thông tin nên giúp người mới đến xác định vị trí và hướng đi tiếp theo. Ký hiệu nhất quán và chữ dễ đọc hỗ trợ cả người quen lẫn khách lần đầu ghé thăm."),
         ("Giữ lối đi thông thoáng trong hoạt động cộng đồng", "Khi tổ chức một hoạt động trên phố, cần tính cả khu vực tập trung và phần dành cho người qua lại. Sự phân chia rõ giúp các nhu cầu sử dụng cùng tồn tại thuận tiện hơn."),
     ]),
    ("Xã hội", 27, "Một con phố với nhà ở và cửa hàng tại Thành phố Hồ Chí Minh",
     "Đường phố khu dân cư thường kết hợp nhà ở, cửa hàng và hoạt động đi lại. Mỗi mặt tiền góp vào cách khu phố vận hành trong đời sống hằng ngày.", [
         ("Nhà ở và cửa hàng cùng tạo nên diện mạo khu phố", "Ở nhiều tuyến phố, tầng trệt được dùng cho hoạt động kinh doanh còn các tầng trên phục vụ nhu cầu khác. Sự kết hợp này tạo ra nhịp hoạt động riêng cho từng đoạn đường."),
         ("Ghi lại thay đổi đô thị qua ảnh đường phố", "Ảnh chụp ở cùng một vị trí vào những thời điểm khác nhau giúp nhận ra thay đổi về mặt tiền và cách sử dụng đường. Để so sánh, cần giữ thông tin thời gian và vị trí chụp."),
         ("Cửa hàng nhỏ trong mạng lưới dịch vụ khu dân cư", "Những cửa hàng gần nơi ở phục vụ các nhu cầu thường ngày. Quan sát tuyến phố cho thấy sự liên kết giữa hoạt động mua bán và hành trình đi lại của cư dân."),
         ("Không gian trước cửa nhà và phần đường dùng chung", "Khu vực tiếp giáp giữa nhà ở và đường phố có nhiều người cùng sử dụng. Cách sắp xếp đồ vật và phương tiện ảnh hưởng trực tiếp đến phần lối đi còn lại."),
     ]),
    ("Xã hội", 28, "Dãy nhà và tán cây ven đường trong khu phố",
     "Diện mạo một tuyến phố được hình thành từ công trình, cây xanh và hoạt động của cư dân. Những chi tiết quen thuộc có thể trở thành tư liệu khi ghi chép về đời sống đô thị.", [
         ("Hàng cây và mặt tiền nhà trong bức tranh đô thị", "Tán cây và công trình tạo nên những lớp không gian khác nhau khi nhìn từ đường phố. Ảnh tư liệu giúp mô tả mối quan hệ này mà không cần coi một góc phố là đại diện cho toàn thành phố."),
         ("Tìm hiểu khu phố bằng cách quan sát những chi tiết nhỏ", "Biển hiệu, lối vào và khoảng trống giữa các công trình cho biết cách không gian được sử dụng. Ghi chép cụ thể giúp tách điều quan sát được khỏi những giả định của người viết."),
         ("Ký ức khu phố có thể được lưu bằng ảnh như thế nào?", "Một bộ ảnh có chú thích về địa điểm và thời gian sẽ dễ tra cứu hơn ảnh rời rạc. Cư dân cũng có thể bổ sung thông tin để làm rõ bối cảnh của từng khung hình."),
         ("Chú thích ảnh đời sống: mô tả đúng thay vì suy đoán", "Người viết nên ghi những gì có thể nhận diện trong ảnh và nêu rõ khi đây là ảnh minh họa. Không nên gán nghề nghiệp hay câu chuyện cá nhân cho người xuất hiện khi chưa có thông tin."),
     ]),
    ("Đời sống", 29, "Người chuẩn bị bánh và thực phẩm trong khu bếp",
     "Một khu bếp vận hành thuận tiện cần có sự chuẩn bị về nguyên liệu và dụng cụ. Cách sắp xếp công việc giúp người nấu theo dõi nhiều bước mà không bỏ sót phần đang thực hiện.", [
         ("Chuẩn bị nguyên liệu trước khi bắt đầu nấu ăn", "Đọc hết các bước và chia sẵn nguyên liệu giúp người nấu biết thứ tự thao tác. Những phần dùng sau nên được đặt ở vị trí riêng để tránh nhầm với nguyên liệu đã xử lý."),
         ("Sắp xếp dụng cụ để khu bếp gọn và dễ thao tác", "Dụng cụ dùng thường xuyên cần dễ lấy và được trả về vị trí sau khi sử dụng. Bề mặt làm việc thông thoáng giúp quan sát nguyên liệu và giảm thao tác tìm kiếm giữa lúc nấu."),
         ("Làm bánh theo mẻ: vì sao cần thống nhất kích thước?", "Các phần bánh có kích thước gần nhau giúp theo dõi quá trình chế biến thuận tiện hơn. Người làm cần ghi lại lượng nguyên liệu và cách chia phần để có thể lặp lại công thức."),
         ("Phân chia công việc khi nhiều người cùng vào bếp", "Mỗi người có thể phụ trách một bước như chuẩn bị, chế biến hoặc dọn dụng cụ. Trao đổi trước về thứ tự dùng bếp và mặt bàn giúp tránh cản trở nhau trong không gian nhỏ."),
     ]),
    ("Đời sống", 30, "Mọi người cùng sơ chế rau củ và chuẩn bị món ăn",
     "Chuẩn bị bữa ăn cùng nhau là dịp phân chia công việc trong gia đình. Rau củ, dụng cụ và khu vực sơ chế cần được tổ chức phù hợp với món dự định thực hiện.", [
         ("Cùng chuẩn bị bữa ăn: bắt đầu từ việc chia công đoạn", "Người tham gia có thể chọn phần việc phù hợp như rửa rau, chuẩn bị dụng cụ hoặc sắp bàn. Việc thống nhất món trước giúp các công đoạn liên kết thay vì mỗi người làm theo một hướng."),
         ("Danh sách nguyên liệu giúp buổi nấu ăn bớt lúng túng", "Danh sách nên ghi lượng dự kiến và những thứ đã có sẵn. Khi đổi món, cập nhật danh sách giúp tránh mua trùng hoặc thiếu nguyên liệu cho bước chế biến chính."),
         ("Tổ chức khu vực sơ chế rau củ trong căn bếp nhỏ", "Một mặt bàn có thể chia thành phần nguyên liệu chờ xử lý và phần đã hoàn thành. Dụng cụ được sắp theo thứ tự sử dụng giúp người cùng làm dễ hiểu tiến độ."),
         ("Ghi chép công thức gia đình để lần sau dễ thực hiện", "Bên cạnh nguyên liệu, nên ghi cả thứ tự thao tác và những thay đổi đã thử. Một ghi chép cụ thể giúp các thành viên khác thực hiện lại món mà không phải đoán từ trí nhớ."),
     ]),
    ("Đời sống", 31, "Một đĩa salad rau xanh đặt trên bàn",
     "Salad là cách kết hợp nhiều loại rau và nguyên liệu trong cùng một món. Hương vị và cách trình bày thay đổi theo thành phần cũng như thứ tự chuẩn bị.", [
         ("Một đĩa salad bắt đầu từ cách chọn thành phần", "Có thể chia thành phần theo vai trò như phần rau nền, phần tạo độ giòn và phần gia vị. Cách phân chia giúp người nấu thử phối hợp mà vẫn theo dõi được nguyên nhân làm hương vị thay đổi."),
         ("Vì sao nên cân nhắc thời điểm trộn nước xốt salad?", "Sau khi trộn, kết cấu món có thể thay đổi theo thời gian. Chuẩn bị riêng các phần rồi kết hợp gần lúc dùng giúp dễ kiểm soát trải nghiệm của món theo công thức đã chọn."),
         ("Trình bày món rau bằng màu sắc và khoảng trống", "Màu của từng nguyên liệu có thể tạo điểm nhấn mà không cần quá nhiều đồ trang trí. Chọn bát đĩa vừa với lượng món giúp các thành phần dễ nhìn và thuận tiện khi dùng."),
         ("Ghi lại cách phối salad để tìm hương vị yêu thích", "Mỗi lần thử có thể thay một thành phần hoặc lượng xốt thay vì đổi tất cả. Ghi chép ngắn giúp nhận ra sự khác nhau giữa các lần và tái hiện cách phối phù hợp với khẩu vị."),
     ]),
    ("Đời sống", 32, "Các loại củ và rau tươi được bày bán tại chợ",
     "Một quầy rau có nhiều loại nguyên liệu với hình dáng và cách sử dụng khác nhau. Lên kế hoạch món ăn trước khi đi chợ giúp việc lựa chọn có mục đích rõ ràng hơn.", [
         ("Đi chợ theo thực đơn: lựa chọn rau củ có kế hoạch", "Danh sách món giúp xác định những loại rau củ cần dùng chung cho nhiều bữa. Trước khi mua, kiểm tra phần còn lại trong bếp để điều chỉnh lượng phù hợp với nhu cầu gia đình."),
         ("Quan sát màu sắc và hình dáng khi tìm hiểu rau củ", "Rau củ trong cùng một quầy có thể được nhóm theo loại hoặc cách sử dụng. Người mới nấu ăn có thể ghi lại tên và món dự định làm để dễ hỏi thêm thông tin khi mua."),
         ("Từ quầy rau đến căn bếp: sắp xếp nguyên liệu sau khi mua", "Sau khi về nhà, phân loại nguyên liệu theo món và thời điểm dự định dùng giúp dễ theo dõi. Ghi ngày mua và lượng còn lại là cách đơn giản để tránh bỏ quên ở góc tủ."),
         ("Một chuyến đi chợ gọn hơn nhờ danh sách mua sắm", "Có thể nhóm danh sách theo quầy hàng để giảm việc quay lại nhiều lần. Khi một nguyên liệu không có, việc biết vai trò của nó trong món giúp cân nhắc phương án thay thế phù hợp."),
     ]),
]


def build_catalog():
    from data.article_details import DETAILS, TAGS
    buckets = {}
    for category, number, caption, intro, angles in TOPICS:
        for index, (title, focus) in enumerate(angles):
            detail, practice = DETAILS[number]
            companion = angles[(index + 1) % len(angles)][1]
            closing = angles[(index + 2) % len(angles)][1]
            context = angles[(index + 3) % len(angles)][1]
            buckets.setdefault(category, []).append({
                "title": title, "summary": focus, "category": category,
                "image": f"/static/images/news_{number:03d}.jpg",
                "image_alt": caption, "image_caption": caption + ". Ảnh minh họa từ kho ảnh mở.",
                "content": f"{intro}\n\n{context}\n\n## Góc nhìn từ thực tế\n\n"
                           f"{detail}\n\n{companion}\n\n## Những điều cần lưu ý\n\n"
                           f"{practice}\n\n{closing}",
                "tags": [category, *TAGS[number]],
                "status": "published", "seed_version": 3,
            })
    result = []
    # Alternate subjects within a category, so a section does not repeat one photo.
    for category, items in buckets.items():
        if category == "Khoa học":
            items = items[-4:] + items[:-4]
        buckets[category] = [items[index] for angle in range(4)
                             for index in range(angle, len(items), 4)]
    while any(buckets.values()):
        for items in buckets.values():
            if items:
                result.append(items.pop(0))
    return result
