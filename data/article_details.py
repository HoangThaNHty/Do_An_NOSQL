"""Các đoạn triển khai riêng cho từng chủ đề trong bộ bài kiến thức mẫu."""
TAGS = {
    1: ["máy chủ", "trung tâm dữ liệu"], 2: ["phần mềm", "ứng dụng web"],
    3: ["JavaScript", "giao diện"], 5: ["điện thoại", "đọc tin"],
    6: ["chứng khoán", "sàn giao dịch"], 7: ["dữ liệu thị trường", "biểu đồ"],
    9: ["container", "logistics", "cảng biển"], 10: ["container", "vận tải", "cảng biển"],
    11: ["bóng bầu dục", "đội hình"], 12: ["bóng đá", "sân vận động"],
    13: ["sân thể thao", "khán đài"], 14: ["sân vận động", "khán giả"],
    16: ["thiên hà", "thiên văn"], 17: ["tinh vân", "vũ trụ"],
    18: ["SOFIA", "máy bay nghiên cứu", "thiên văn"], 19: ["vũ trụ", "ảnh thiên văn"],
    20: ["ngắm sao", "quan sát bầu trời"], 21: ["phố đêm", "đô thị"],
    22: ["phố đi bộ", "không gian công cộng"], 27: ["khu phố", "đời sống đô thị"],
    28: ["ảnh tư liệu", "ký ức đô thị"], 29: ["nấu ăn", "khu bếp"],
    30: ["bữa ăn", "gia đình"], 31: ["salad", "rau xanh"], 32: ["đi chợ", "rau củ"],
}

DETAILS = {
    1: (
        "Điều dễ nhận thấy trong một phòng máy là mật độ thiết bị khá lớn, nhưng việc vận hành không chỉ nằm ở số lượng máy chủ. Nhân viên cần biết thiết bị nào phục vụ ứng dụng nào, đường kết nối đi qua đâu và ai chịu trách nhiệm khi xuất hiện cảnh báo. Một sơ đồ rõ ràng vì vậy có giá trị ngay cả khi hệ thống còn nhỏ.",
        "Khi bổ sung một máy chủ, nhóm vận hành thường phải xem xét đồng thời chỗ đặt, đường điện, kết nối mạng và không gian bảo trì. Nếu chỉ lắp thiết bị vào vị trí còn trống, những lần kiểm tra sau có thể trở nên khó khăn. Cách tổ chức có hệ thống giúp việc mở rộng bớt phụ thuộc vào trí nhớ của từng người.",
    ),
    2: (
        "Có thể hình dung luồng xử lý qua một trang tin: trình duyệt yêu cầu bài viết, máy chủ kiểm tra dữ liệu và trả nội dung để hiển thị. Nếu một bài được nhiều người mở liên tục, những thao tác lặp lại sẽ trở thành nơi cần quan sát. Nhóm phát triển cần xác định bước nào thực sự tốn thời gian trước khi chọn cách cải thiện.",
        "Một thay đổi nên được kiểm tra bằng tình huống cụ thể thay vì chỉ nhìn thông báo thành công. Chẳng hạn, sau khi sửa bài, hãy mở lại nội dung ở một phiên khác; sau khi xóa, thử truy cập đường dẫn cũ. Những thao tác nhỏ này giúp phát hiện khoảng cách giữa kết quả ở cơ sở dữ liệu và trải nghiệm thực tế trên trang.",
    ),
    3: (
        "Một biểu mẫu dễ dùng cần phản hồi đúng thời điểm. Khi người dùng đang nhập, gợi ý ngắn có thể giúp họ sửa sớm; khi đã gửi, trạng thái chờ cần đủ rõ để tránh bấm lặp. Trường hợp máy chủ trả lỗi cũng phải được tính đến, bởi kết nối tốt trong lúc phát triển không đại diện cho mọi lần truy cập.",
        "Với chức năng tìm kiếm, phản hồi nhanh còn đòi hỏi kiểm soát thứ tự yêu cầu. Người dùng có thể gõ thêm vài ký tự trước khi kết quả trước đó trở về. Nếu giao diện không phân biệt yêu cầu cũ và mới, danh sách gợi ý dễ hiển thị sai từ khóa. Chỉ cập nhật kết quả của lượt nhập hiện tại sẽ tạo cảm giác nhất quán hơn.",
    ),
    5: (
        "Trên màn hình nhỏ, mỗi thành phần đều cạnh tranh diện tích với phần nội dung. Một thanh điều hướng dài hoặc ảnh quá cao có thể khiến người đọc phải cuộn nhiều trước khi biết bài nói về điều gì. Bố cục cần giữ được thứ tự thông tin, đồng thời cho phép mở menu, tìm kiếm và quay lại danh sách bằng những thao tác đơn giản.",
        "Việc kiểm tra nên bắt đầu từ một hành trình thật: mở trang chủ, chọn bài, đọc vài đoạn rồi tìm bài khác. Trong quá trình đó, cần quan sát xem bàn phím có che gợi ý tìm kiếm hay nút bấm có nằm quá gần nhau không. Những điểm vướng nhỏ thường chỉ lộ ra khi sử dụng liên tiếp nhiều màn hình.",
    ),
    6: (
        "Trong ảnh tư liệu về sàn giao dịch, nhiều hoạt động diễn ra cùng lúc trong một không gian tập trung. Người xem có thể chú ý đến cách các nhóm đứng quanh vị trí làm việc, thay vì cố suy ra diễn biến thị trường từ nét mặt hay số người xuất hiện. Hình ảnh cung cấp bối cảnh, còn giá và khối lượng cần được đọc từ dữ liệu riêng.",
        "Khi tìm hiểu một cơ chế giao dịch, ví dụ nhỏ thường dễ theo dõi hơn những con số tổng hợp. Hãy phân biệt thời điểm gửi lệnh, trạng thái đang chờ và thời điểm giao dịch được ghi nhận. Việc tách các bước giúp người đọc hiểu vì sao một yêu cầu mua hoặc bán không đồng nghĩa với giao dịch đã hoàn tất.",
    ),
    7: (
        "Một bảng số liệu chỉ hữu ích khi người đọc hiểu điều đang được đo. Cùng một cột phần trăm có thể thể hiện thay đổi theo ngày, theo tháng hoặc so với một mốc khác. Nếu bỏ qua phần chú giải, hai con số trông giống nhau có thể bị đặt cạnh nhau dù thực chất đang mô tả những khoảng thời gian khác nhau.",
        "Cách trình bày cũng ảnh hưởng đến cảm nhận về thông tin. Tiêu đề, màu sắc và phạm vi trục có thể khiến người đọc chú ý nhiều hơn vào một phần biến động. Vì vậy, khi đọc một bài phân tích, nên đối chiếu lời diễn giải với bảng dữ liệu và kiểm tra những giới hạn mà tác giả đã nêu.",
    ),
    9: (
        "Một container đến cảng chưa phải đã kết thúc hành trình. Hàng còn cần được nhận diện, đưa về khu vực phù hợp và bàn giao cho chặng vận chuyển tiếp theo. Nếu thông tin giữa tàu, bãi và bên nhận không khớp, thời gian chờ có thể xuất hiện dù thiết bị bốc dỡ vẫn đang hoạt động bình thường.",
        "Trong một ví dụ đơn giản, xe đến nhận hàng cần biết container đã sẵn sàng hay chưa và phải đi đến khu vực nào. Thông báo thay đổi lịch cần đến đúng người để họ điều chỉnh kế hoạch. Dòng dữ liệu rõ ràng vì thế là phần đi cùng dòng hàng hóa, chứ không chỉ là công việc ghi chép sau khi giao nhận xong.",
    ),
    10: (
        "Tại bãi cảng, khoảng cách di chuyển và thứ tự lấy hàng có thể tạo khác biệt trong công việc hằng ngày. Một container đặt ở vị trí thuận tiện cho lúc dỡ tàu chưa chắc thuận tiện cho lúc xe đến nhận. Kế hoạch sắp xếp cần nhìn vào cả bước hiện tại lẫn những bước sẽ diễn ra sau đó.",
        "Khi xuất hiện ùn chờ, tổng thời gian chỉ cho biết có vấn đề mà chưa chỉ ra nguyên nhân. Tách thời gian tại cổng, thời gian tìm vị trí và thời gian nâng hạ giúp người vận hành có bức tranh cụ thể hơn. Từ đó, việc điều chỉnh có thể tập trung vào đúng khu vực thay vì thay đổi toàn bộ quy trình.",
    ),
    11: (
        "Ở góc nhìn rộng, người xem có thể theo dõi cách các cầu thủ chuẩn bị trước khi tình huống bắt đầu. Những bước dịch chuyển nhỏ cho thấy đội hình không phải một hình vẽ cố định. Khi chỉ xem đoạn cận cảnh theo bóng, phần chuẩn bị này thường dễ bị bỏ qua dù nó giúp giải thích hướng phát triển của pha đấu.",
        "Với người mới làm quen, không cần ghi nhớ mọi chi tiết ngay trong lần xem đầu tiên. Có thể chọn quan sát một nhóm cầu thủ hoặc một khu vực sân, rồi đối chiếu cách họ thay đổi vị trí giữa các lượt chơi. Cách xem có trọng tâm giúp trận đấu bớt rối và tạo nền để tìm hiểu thêm về luật.",
    ),
    12: (
        "Trải nghiệm ở sân bắt đầu từ trước lúc trận đấu diễn ra. Khán giả cần tìm cửa vào, xác định khu ghế và có đủ thông tin để di chuyển mà không phải hỏi nhiều lần. Khi lượng người đến tăng trong thời gian ngắn, những chi tiết như biển chỉ dẫn và vị trí nhân viên hỗ trợ trở nên dễ nhận thấy hơn.",
        "Trong khung cảnh thi đấu buổi tối, ánh sáng trên mặt sân tạo điểm tập trung nhưng không phải khu vực duy nhất cần được quan tâm. Hành lang, bậc lên xuống và đường kết nối giữa các khu ghế cũng thuộc hành trình sử dụng. Một sự kiện được chuẩn bị tốt là kết quả phối hợp của nhiều phần việc ít xuất hiện trên màn hình truyền hình.",
    ),
    13: (
        "Không gian ngoài trời khiến sân đấu gắn rõ với cảnh quan xung quanh. Từ trên khán đài, người xem có thể nhìn thấy cả khu vực thi đấu lẫn phần địa hình phía xa. Hình ảnh đó tạo nét riêng cho địa điểm, nhưng việc tổ chức vẫn cần dựa trên điều kiện sử dụng cụ thể của sân và các khu phụ trợ.",
        "Khi chuẩn bị cho ngày có sự kiện, nhóm vận hành cần kiểm tra cách người tham dự tiếp cận khu vực ghế ngồi và những điểm dễ tập trung đông. Sơ đồ rõ ràng giúp người mới đến hình dung được đường đi trước khi bước vào khu khán đài. Đây là phần bổ sung cần thiết bên cạnh việc chuẩn bị bề mặt thi đấu.",
    ),
    14: (
        "Nhìn từ một tầng khán đài, khoảng cách đến sân không chỉ được đo bằng số hàng ghế. Góc nhìn còn chịu ảnh hưởng bởi hướng ngồi, lan can và các phần công trình nằm phía trước. Vì vậy, một ảnh toàn cảnh có thể giúp giới thiệu không gian nhưng chưa thay thế được sơ đồ vị trí chi tiết.",
        "Ở thời điểm nhiều khán giả cùng đứng dậy, hành lang và lối nối giữa các khu vực trở thành phần quan trọng của trải nghiệm. Việc chỉ dẫn cần nhất quán từ vé, cửa vào đến hàng ghế. Nếu cách gọi khu vực thay đổi giữa các điểm, người sử dụng dễ mất phương hướng dù khoảng cách di chuyển không lớn.",
    ),
    16: (
        "Điểm hấp dẫn của ảnh thiên hà nằm ở sự tương phản giữa vùng trung tâm và những cấu trúc trải rộng ra xung quanh. Thay vì chỉ nhìn tổng thể như một hình xoắn, người đọc có thể chú ý đến vùng sáng, dải tối và những đường nét nối tiếp nhau. Mỗi phần gợi ra một câu hỏi khác nhau về đối tượng đang được quan sát.",
        "Tuy nhiên, ảnh đẹp không tự cung cấp đầy đủ lời giải. Thông tin về nguồn ảnh, bộ lọc và quá trình xử lý giúp người xem biết đâu là dữ liệu thu nhận và đâu là cách biểu diễn. Đọc cả phần chú thích sẽ tạo nền vững hơn cho việc tìm hiểu tiếp, thay vì suy đoán tính chất của thiên hà chỉ từ màu sắc.",
    ),
    17: (
        "Trong ảnh tinh vân, những vùng sáng đậm và nhạt tạo cảm giác như các lớp mây chồng lên nhau. Người xem có thể bắt đầu bằng việc nhận diện ranh giới giữa vùng khí và nền sao. Đây là cách quan sát trực quan, giúp hình dung câu hỏi nghiên cứu trước khi đi sâu vào các thuật ngữ chuyên môn.",
        "Một điều cần lưu ý là cách tạo ảnh có thể khác với trải nghiệm nhìn bằng mắt thường. Màu được dùng để thể hiện tín hiệu thu qua các bộ lọc, nên chú thích kỹ thuật là phần rất đáng đọc. Khi chia sẻ ảnh, giữ lại thông tin nguồn và phương pháp thể hiện cũng giúp người xem sau tránh hiểu sai hình ảnh.",
    ),
    18: (
        "Hình ảnh một chiếc máy bay mang thiết bị nghiên cứu cho thấy công cụ khoa học có thể được thiết kế theo nhiều hình thức. Bên cạnh yêu cầu quan sát, nền tảng này còn có những phần việc thuộc vận hành phương tiện. Điều đó làm nổi bật vai trò phối hợp giữa các nhóm có chuyên môn và lịch làm việc khác nhau.",
        "Để hiểu một nhiệm vụ, người đọc nên tách ba câu hỏi: muốn quan sát điều gì, dùng thiết bị nào và cần điều kiện nào để thu dữ liệu. Bắt đầu từ mục tiêu sẽ giúp việc tìm hiểu cấu tạo bớt rời rạc. Ảnh phương tiện là điểm mở đầu sinh động, còn mô tả nhiệm vụ mới giúp giải thích vì sao nó được lựa chọn.",
    ),
    19: (
        "Một ảnh không gian nhiều màu thường thu hút ánh nhìn ngay lập tức, nhưng những vùng màu khác nhau cần được đọc cùng phần giải thích đi kèm. Người tạo ảnh có thể kết hợp nhiều lớp dữ liệu để làm rõ cấu trúc. Nếu chỉ giữ hình mà bỏ chú thích, người xem dễ mất phần thông tin quan trọng nhất về cách ảnh được hình thành.",
        "Có thể tiếp cận hình ảnh theo từng bước: quan sát các vùng nổi bật, tìm nguồn dữ liệu, rồi đọc mô tả quá trình xử lý. Cách đi từ điều nhìn thấy đến thông tin nền giúp phân biệt quan sát với diễn giải. Nó cũng nhắc rằng một bức ảnh khoa học vừa là phương tiện truyền đạt, vừa cần được đặt trong bối cảnh nghiên cứu.",
    ),
    20: (
        "Đối với một buổi quan sát bầu trời, địa điểm gần gũi vẫn có những yếu tố cần khảo sát trước. Người tham gia cần biết hướng nhìn có bị công trình hoặc tán cây che khuất không, khu vực nào thuận tiện đặt thiết bị và có thể di chuyển ra vào bằng cách nào. Những ghi nhận này giúp buổi hoạt động diễn ra chủ động hơn.",
        "Việc lưu nhật ký không đòi hỏi cách trình bày phức tạp. Một bản ghi về thời gian, điều kiện bầu trời và những gì đã quan sát được đã có ích cho lần đối chiếu sau. Khi chia sẻ trải nghiệm, nêu rõ giới hạn của địa điểm cũng giúp người khác hiểu vì sao cùng một thiết bị có thể mang lại kết quả khác ở nơi khác.",
    ),
    21: (
        "Khi trời tối, những chi tiết quen thuộc của đường phố có thể trở nên khó nhận biết hơn. Người đi bộ phải quan sát đồng thời mặt đường, phương tiện và vị trí chuyển tiếp giữa các khu vực. Một đoạn đường thuận tiện vào ban ngày vì thế vẫn cần được nhìn lại ở thời điểm có điều kiện ánh sáng khác.",
        "Ảnh phố đêm cũng cho thấy nhiều hoạt động cùng sử dụng một không gian: mua bán, đi lại và tiếp cận nhà ở. Muốn mô tả đầy đủ, người viết cần ghi nhận cả vị trí lẫn thời điểm quan sát. Việc tránh suy rộng từ một khung hình giúp câu chuyện về đô thị giữ được sự cụ thể và gần với đời sống hơn.",
    ),
    22: (
        "Một tuyến phố dành chỗ cho việc đi bộ có thể phục vụ nhiều nhịp sinh hoạt. Có người đi qua nhanh, có người dừng trò chuyện hoặc ngắm cảnh. Cách bố trí không gian cần cân nhắc những nhu cầu này thay vì xem tất cả người sử dụng như đang thực hiện cùng một hành trình.",
        "Các chi tiết nhỏ như nơi nghỉ chân, bóng cây và biển chỉ dẫn có thể ảnh hưởng đến thời gian người dân muốn ở lại. Khi có hoạt động cộng đồng, khoảng trống di chuyển cũng cần được giữ rõ. Quan sát cách không gian được dùng vào nhiều thời điểm sẽ cho bức tranh đầy đủ hơn so với một lần ghé thăm.",
    ),
    27: (
        "Ở một khu phố có nhà ở kết hợp kinh doanh, nhịp sống thường thay đổi theo giờ mở cửa và lịch sinh hoạt. Phần đường trước cửa nhà vừa là lối tiếp cận vừa có thể trở thành nơi dừng xe hoặc giao nhận hàng. Chính những hoạt động thường ngày này làm nên diện mạo sống động của tuyến phố.",
        "Để lưu lại sự thay đổi, một bộ ảnh nên đi kèm ghi chép về vị trí, thời gian và hướng chụp. Sau này, người xem có thể đối chiếu mặt tiền, biển hiệu hoặc cách sử dụng khoảng trống. Ghi nhận rõ ràng giúp tư liệu giữ được giá trị kể cả khi người chụp không còn nhớ đầy đủ bối cảnh.",
    ),
    28: (
        "Không phải thay đổi nào của một khu phố cũng diễn ra ở quy mô lớn. Một cửa hàng mới, phần mặt tiền được sửa lại hay tán cây thay đổi đã có thể tác động đến cảm nhận của người đi qua. Những chi tiết nhỏ đáng được ghi chép nếu mục tiêu là hiểu đời sống thường ngày của một nơi chốn.",
        "Trong quá trình kể chuyện bằng ảnh, thông tin của cư dân có thể bổ sung điều khung hình không thể hiện. Dù vậy, cần phân biệt lời kể, ký ức và những chi tiết đã kiểm tra được. Cách trình bày rõ nguồn của từng thông tin giúp câu chuyện giàu bối cảnh mà vẫn giữ được sự thận trọng cần thiết.",
    ),
    29: (
        "Một buổi vào bếp thường dễ theo dõi hơn khi người nấu hình dung trước toàn bộ công việc. Những bước như chuẩn bị khay, chia nguyên liệu và dọn chỗ đặt dụng cụ có vẻ nhỏ nhưng lại ảnh hưởng đến nhịp thao tác. Nếu phải dừng liên tục để tìm đồ, phần việc đang làm dễ bị gián đoạn.",
        "Với món thực hiện nhiều lần, ghi chép ngắn sau khi nấu giúp rút kinh nghiệm cho lần tiếp theo. Có thể lưu lượng nguyên liệu đã dùng, cách chia phần và điều muốn thay đổi. Những ghi nhận thực tế thường dễ áp dụng hơn một nhận xét chung rằng món hôm nay thành công hoặc chưa như mong muốn.",
    ),
    30: (
        "Khi nhiều người cùng chuẩn bị bữa ăn, điều cần thống nhất trước tiên là thứ tự dùng không gian. Một mặt bàn có thể vừa là nơi đặt rau đã rửa vừa là chỗ cắt và chia phần. Phân biệt các khu vực và báo cho nhau khi chuyển công đoạn giúp công việc liền mạch hơn, nhất là trong căn bếp nhỏ.",
        "Bữa ăn chung cũng là dịp truyền lại những kinh nghiệm khó ghi hết trong công thức. Người quen việc có thể giải thích vì sao chọn cách cắt hoặc thứ tự cho nguyên liệu. Kết hợp lời hướng dẫn với ghi chép cụ thể giúp các thành viên khác tự thực hiện được món trong những lần sau.",
    ),
    31: (
        "Một món salad có thể được điều chỉnh theo nguyên liệu đang có mà vẫn giữ được ý tưởng ban đầu. Thay vì thêm nhiều thứ cùng lúc, người nấu có thể xác định phần rau nền rồi chọn điểm nhấn về độ giòn, vị hoặc màu sắc. Cách làm này giúp dễ nhận ra thành phần nào đang chi phối hương vị.",
        "Khi muốn thử một cách phối mới, thay đổi từng yếu tố sẽ giúp so sánh rõ hơn. Có thể giữ nguyên phần rau và đổi lượng xốt, hoặc giữ xốt nhưng thử một nguyên liệu khác. Ghi lại cảm nhận sau mỗi lần thực hiện giúp hình thành công thức phù hợp với khẩu vị của người dùng món.",
    ),
    32: (
        "Chuyến đi chợ thường gọn hơn khi gắn với kế hoạch sử dụng nguyên liệu. Trước khi mua, việc nhìn lại những gì còn trong bếp giúp tránh chọn thêm chỉ vì thấy quầy hàng hấp dẫn. Một loại rau củ dùng được cho vài món dự kiến có thể giúp danh sách đơn giản và dễ theo dõi hơn.",
        "Sau khi mang nguyên liệu về, câu chuyện chuyển sang cách sắp xếp và ghi nhớ. Nhóm những phần cần dùng cho cùng một món, ghi lại ngày mua hoặc đánh dấu phần dự định dùng trước là những việc nhỏ nhưng thiết thực. Nhờ đó, kế hoạch từ lúc đi chợ có cơ hội được thực hiện thay vì bị bỏ quên sau một ngày bận rộn.",
    ),
}
