# -*- coding: utf-8 -*-
"""
scripts/build_part7_questions.py
================================
Defines all 54 questions for TOEIC Part 7 (Questions 147 to 200).
Strictly matches official answer key:
147: A, 148: B
149: B, 150: C
151: C, 152: B, 153: D
154: D, 155: C
156: C, 157: D
158: C, 159: B, 160: C, 161: A
162: A, 163: B, 164: D, 165: D
166: C, 167: A, 168: D
169: A, 170: C, 171: C
172: B, 173: C, 174: D, 175: A
176: C, 177: A, 178: B, 179: D, 180: C
181: A, 182: B, 183: B, 184: D, 185: D
186: C, 187: A, 188: C, 189: B, 190: A
191: B, 192: B, 193: D, 194: A, 195: D
196: C, 197: A, 198: D, 199: B, 200: C
"""

part7_questions = [
    # -------------------------------------------------------------------------
    # Group 1: 147-148 (test1-p7-g147_148)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q147",
        "group_id": "test1-p7-g147_148",
        "part": 7,
        "question_number": 147,
        "question_type_tag": "detail_lookup",
        "question_text": "What is indicated about Harbis Stationery Store?",
        "options": {
            "A": "It provides materials for students.",
            "B": "It has stores in multiple locations.",
            "C": "It is celebrating an anniversary.",
            "D": "It provides free shipping for online orders."
        },
        "correct_answer": "A",
        "evidence_quote": "All School Supplies 10% Off",
        "paraphrase_pair": {
            "original": "All School Supplies",
            "paraphrased": "materials for students"
        },
        "explanation_vi": "Phân tích câu hỏi: Điều gì được chỉ ra về cửa hàng Harbis Stationery?\n- Dẫn chứng trong bài: Mục 'All School Supplies 10% Off' giảm giá các mặt hàng gồm: Box of 24 pens, Desk lamp, Wireless mouse, Backpack (đồ dùng học tập, bút viết, ba lô cho học sinh, sinh viên).\n- Phương án đúng: (A) Cửa hàng cung cấp vật dụng, đồ dùng cho học sinh/sinh viên.\n- Bẫy đề thi: (B) 'multiple locations' không hề được đề cập (bài chỉ ghi 500 Pinstone Street); (D) 'free shipping' sai vì bài nêu rõ 'Prices indicated are for in-store purchases only' (chỉ áp dụng mua trực tiếp tại cửa hàng).\n- Mẹo làm bài: Chú ý tiêu đề danh mục 'School supplies' (đồ dùng học tập) tương đương với 'materials for students'."
    },
    {
        "id": "test1-q148",
        "group_id": "test1-p7-g147_148",
        "part": 7,
        "question_number": 148,
        "question_type_tag": "detail_lookup",
        "question_text": "What item is discounted by the greatest percentage?",
        "options": {
            "A": "Box of ten cards",
            "B": "Box of five invitations",
            "C": "Wireless mouse",
            "D": "Desk lamp"
        },
        "correct_answer": "B",
        "evidence_quote": "Box of five customizable seasonal cards or invitations (50% off)",
        "paraphrase_pair": {
            "original": "invitations (50% off)",
            "paraphrased": "discounted by the greatest percentage"
        },
        "explanation_vi": "Phân tích câu hỏi: Mặt hàng nào được giảm giá theo tỷ lệ phần trăm lớn nhất (greatest percentage)?\n- Dẫn chứng trong bài:\n  + Box of ten preprinted seasonal cards: 25% off\n  + Box of five customizable seasonal cards or invitations: 50% off\n  + Wireless mouse / Desk lamp (thuộc mục All school supplies): 10% off\n- So sánh phần trăm: 50% là mức giảm giá cao nhất.\n- Phương án đúng: (B) Hộp 5 thiệp mời (Box of five invitations).\n- Bẫy đề thi: Cần phân biệt rõ giữa 'greatest percentage' (tỷ lệ phần trăm lớn nhất - 50%) và số tiền giảm giá hoặc giá thành sản phẩm."
    },

    # -------------------------------------------------------------------------
    # Group 2: 149-150 (test1-p7-g149_150)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q149",
        "group_id": "test1-p7-g149_150",
        "part": 7,
        "question_number": 149,
        "question_type_tag": "intent",
        "question_text": "What is the purpose of the e-mail?",
        "options": {
            "A": "To inquire about leasing a vehicle",
            "B": "To inform a customer of required car maintenance",
            "C": "To announce the release of a new car",
            "D": "To register a used car for an extended warranty"
        },
        "correct_answer": "B",
        "evidence_quote": "Your car is now due for its required annual service and maintenance check.",
        "paraphrase_pair": {
            "original": "due for its required annual service and maintenance check",
            "paraphrased": "inform a customer of required car maintenance"
        },
        "explanation_vi": "Phân tích câu hỏi: Mục đích chính của bức email là gì?\n- Dẫn chứng trong bài: 'Your car is now due for its required annual service and maintenance check. To book your appointment, please call us...' (Xe của bạn hiện đã đến hạn kiểm tra bảo dưỡng và dịch vụ định kỳ bắt buộc hàng năm).\n- Phương án đúng: (B) Thông báo cho khách hàng về việc bảo dưỡng xe bắt buộc.\n- Bẫy đề thi: (A) hỏi về việc thuê xe (ông Peng đã thuê xe từ năm ngoái rồi); (C) thông báo ra mắt xe mới; (D) đăng ký gia hạn bảo hành xe cũ (sai nội dung)."
    },
    {
        "id": "test1-q150",
        "group_id": "test1-p7-g149_150",
        "part": 7,
        "question_number": 150,
        "question_type_tag": "inference",
        "question_text": "What is indicated about Chen Construction?",
        "options": {
            "A": "It performs the servicing of its company vehicles.",
            "B": "It has a new project beginning March 1.",
            "C": "It provides leased cars to some employees.",
            "D": "It will soon begin a construction project for Toshi Auto Group."
        },
        "correct_answer": "C",
        "evidence_quote": "Toshi Auto Group handles all the service needs for cars leased by employees of Chen Construction.",
        "paraphrase_pair": {
            "original": "cars leased by employees of Chen Construction",
            "paraphrased": "provides leased cars to some employees"
        },
        "explanation_vi": "Phân tích câu hỏi: Điều gì được chỉ ra về công ty Chen Construction?\n- Dẫn chứng trong bài: 'Toshi Auto Group handles all the service needs for cars leased by employees of Chen Construction.' (Toshi Auto Group chịu trách nhiệm xử lý toàn bộ nhu cầu bảo dưỡng cho các xe ô tô do nhân viên của công ty Chen Construction thuê).\n- Suy luận logic: Chen Construction có chính sách cung cấp/thuê xe ô tô cho một số nhân viên của họ (như ông Wenbin Peng).\n- Phương án đúng: (C) Công ty cung cấp xe thuê cho một số nhân viên.\n- Bẫy đề thi: (A) Chen Construction tự bảo dưỡng xe (sai, vì Toshi Auto Group làm việc này); (B) dự án mới bắt đầu 1 tháng 3 (1 tháng 3 năm ngoái là ngày ông Peng nhận xe)."
    },

    # -------------------------------------------------------------------------
    # Group 3: 151-153 (test1-p7-g151_153)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q151",
        "group_id": "test1-p7-g151_153",
        "part": 7,
        "question_number": 151,
        "question_type_tag": "intent",
        "question_text": "What is the main purpose of the article?",
        "options": {
            "A": "To promote a new line of cookware",
            "B": "To advertise an orchestra concert",
            "C": "To announce a new series of books",
            "D": "To provide a calendar of local events"
        },
        "correct_answer": "C",
        "evidence_quote": "Tillford Press announced the launch of its new imprint, Tillford Exalt.",
        "paraphrase_pair": {
            "original": "launch of its new imprint, Tillford Exalt. This new line will feature books",
            "paraphrased": "announce a new series of books"
        },
        "explanation_vi": "Phân tích câu hỏi: Mục đích chính của bài báo là gì?\n- Dẫn chứng trong bài: Đoạn 1 nêu rõ 'Tillford Press announced the launch of its new imprint, Tillford Exalt. This new line will feature books promoting healthy lifestyles, memoirs...'\n- Từ vựng chuyên ngành xuất bản: 'imprint' là thương hiệu con/dòng sách xuất bản riêng biệt, tương đương với 'a new series of books'.\n- Phương án đúng: (C) Thông báo về một dòng sách / loạt sách mới.\n- Bẫy đề thi: (A) cookware (chảo nồi - bẫy do có đầu bếp Lain Lai); (B) orchestra concert (bẫy do có nhạc trưởng Seung-Hyun Bae)."
    },
    {
        "id": "test1-q152",
        "group_id": "test1-p7-g151_153",
        "part": 7,
        "question_number": 152,
        "question_type_tag": "detail_lookup",
        "question_text": "What is planned for December?",
        "options": {
            "A": "An awards ceremony",
            "B": "The publication of a life story",
            "C": "The release of a new album",
            "D": "The launch of a celebrity's restaurant"
        },
        "correct_answer": "B",
        "evidence_quote": "Ms. Lai's story of her life and career will be the first to be launched. It is set for release in December.",
        "paraphrase_pair": {
            "original": "Ms. Lai's story of her life and career... release in December",
            "paraphrased": "The publication of a life story"
        },
        "explanation_vi": "Phân tích câu hỏi: Điều gì được lên kế hoạch phát hành vào tháng 12?\n- Dẫn chứng trong bài: Đoạn 2 ghi 'Ms. Lai's story of her life and career will be the first to be launched. It is set for release in December.' (Câu chuyện về cuộc đời và sự nghiệp của cô Lai sẽ được phát hành đầu tiên vào tháng 12).\n- 'Story of life and career' (hồi ký cuộc đời) chính là 'life story' hay 'memoir'.\n- Phương án đúng: (B) Xuất bản cuốn hồi ký về cuộc đời của một người (publication of a life story)."
    },
    {
        "id": "test1-q153",
        "group_id": "test1-p7-g151_153",
        "part": 7,
        "question_number": 153,
        "question_type_tag": "detail_lookup",
        "question_text": "What does Frederick Bissett emphasize about Tillford Exalt?",
        "options": {
            "A": "Its record-breaking sales",
            "B": "Its roots in Manchester",
            "C": "Its focus on fiction and poetry",
            "D": "Its broad range of authors"
        },
        "correct_answer": "D",
        "evidence_quote": "We wanted authors from a wide variety of cultural backgrounds, and we think we're off to a great start",
        "paraphrase_pair": {
            "original": "authors from a wide variety of cultural backgrounds",
            "paraphrased": "broad range of authors"
        },
        "explanation_vi": "Phân tích câu hỏi: Ông Frederick Bissett nhấn mạnh điều gì về Tillford Exalt?\n- Dẫn chứng trong bài: Đoạn 3 dẫn lời ông Bissett: 'We wanted authors from a wide variety of cultural backgrounds, and we think we're off to a great start... authors were not always famous...'\n- Paraphrase: 'a wide variety of' đồng nghĩa hoàn hảo với 'broad range of'.\n- Phương án đúng: (D) Đội ngũ tác giả đa dạng, phong phú (broad range of authors)."
    },

    # -------------------------------------------------------------------------
    # Group 4: 154-155 (test1-p7-g154_155)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q154",
        "group_id": "test1-p7-g154_155",
        "part": 7,
        "question_number": 154,
        "question_type_tag": "detail_lookup",
        "question_text": "What problem does Mr. Skagen mention?",
        "options": {
            "A": "Some new employees are absent.",
            "B": "Some boxes are incorrectly labeled.",
            "C": "A package delivery is delayed.",
            "D": "An access door is malfunctioning."
        },
        "correct_answer": "D",
        "evidence_quote": "the power door at Loading Dock B is acting up",
        "paraphrase_pair": {
            "original": "the power door at Loading Dock B is acting up",
            "paraphrased": "An access door is malfunctioning"
        },
        "explanation_vi": "Phân tích câu hỏi: Ông Skagen đề cập đến vấn đề trục trặc gì?\n- Dẫn chứng trong bài: Tin nhắn lúc 8:58 A.M.: 'I noticed the power door at Loading Dock B is acting up.' và 8:59 A.M. 'When I push the button to open it, it raises all the way up but then drops back down...'\n- Thành ngữ 'acting up' nghĩa là bị trục trặc, hỏng hóc, đồng nghĩa với 'malfunctioning'. 'Power door at Loading Dock B' (cửa cuốn tự động ở khu bốc dỡ B) là 'access door'.\n- Phương án đúng: (D) Cửa ra vào / cửa kho bị trục trặc."
    },
    {
        "id": "test1-q155",
        "group_id": "test1-p7-g154_155",
        "part": 7,
        "question_number": 155,
        "question_type_tag": "intent",
        "question_text": "At 9:02 A.M., what does Mr. Skagen most likely mean when he writes, \"Yes, that works\"?",
        "options": {
            "A": "An electrician has arrived at a work site.",
            "B": "Some equipment is operating smoothly.",
            "C": "Trainees can help with some shipments.",
            "D": "Ms. Sadauskas is well suited for her job."
        },
        "correct_answer": "C",
        "evidence_quote": "You can teach them how to create shipping labels and then have them pack and label this morning's shipments.",
        "paraphrase_pair": {
            "original": "teach them how to create shipping labels and then have them pack and label this morning's shipments",
            "paraphrased": "Trainees can help with some shipments"
        },
        "explanation_vi": "Phân tích câu hỏi ngữ cảnh: Vào lúc 9:02 A.M., khi ông Skagen viết 'Yes, that works', ý ông là gì?\n- Ngữ cảnh hội thoại: Trước đó lúc 9:00 A.M., bà Brenda đề xuất: 'Why don't you bring your trainees to my area? You can teach them how to create shipping labels and then have them pack and label this morning's shipments.' (Sao bạn không đưa học viên sang khu của tôi? Bạn có thể dạy họ in nhãn và đóng gói các đơn hàng sáng nay).\n- Khi ông Skagen trả lời 'Yes, that works', ông đồng ý với kế hoạch để các học viên (trainees) qua phụ giúp đóng gói dán nhãn các kiện hàng (shipments).\n- Phương án đúng: (C) Các thực tập sinh có thể phụ giúp xử lý một số đơn hàng."
    },

    # -------------------------------------------------------------------------
    # Group 5: 156-157 (test1-p7-g156_157)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q156",
        "group_id": "test1-p7-g156_157",
        "part": 7,
        "question_number": 156,
        "question_type_tag": "detail_lookup",
        "question_text": "Why was the form submitted?",
        "options": {
            "A": "An image is not displaying clearly.",
            "B": "A projector needs to be set up.",
            "C": "Audio is not functioning properly.",
            "D": "A microphone needs to be repaired."
        },
        "correct_answer": "C",
        "evidence_quote": "There is a problem with the television audio. When I played an online video, the image was fine, but I could not hear anything.",
        "paraphrase_pair": {
            "original": "problem with the television audio... could not hear anything",
            "paraphrased": "Audio is not functioning properly"
        },
        "explanation_vi": "Phân tích câu hỏi: Tại sao biểu mẫu yêu cầu này được gửi đi?\n- Dẫn chứng trong bài: Phần mô tả nêu 'There is a problem with the television audio. When I played an online video, the image was fine, but I could not hear anything.' (Có vấn đề với âm thanh tivi. Hình ảnh thì ổn nhưng tôi không nghe thấy gì cả).\n- Phương án đúng: (C) Âm thanh hoạt động không bình thường (Audio is not functioning properly).\n- Bẫy đề thi: (A) hình ảnh không rõ (sai, bài ghi 'the image was fine'); (B) máy chiếu; (D) micro."
    },
    {
        "id": "test1-q157",
        "group_id": "test1-p7-g156_157",
        "part": 7,
        "question_number": 157,
        "question_type_tag": "detail_lookup",
        "question_text": "What is Ms. Deckow planning to do next week?",
        "options": {
            "A": "Visit a client site",
            "B": "Deliver a product",
            "C": "Create an online video",
            "D": "Give a presentation"
        },
        "correct_answer": "D",
        "evidence_quote": "I'm supposed to deliver a product demonstration for a client in room 500 next Monday",
        "paraphrase_pair": {
            "original": "deliver a product demonstration for a client",
            "paraphrased": "Give a presentation"
        },
        "explanation_vi": "Phân tích câu hỏi: Cô Deckow dự định làm gì vào tuần tới?\n- Dẫn chứng trong bài: 'I'm supposed to deliver a product demonstration for a client in room 500 next Monday...' (Tôi dự kiến sẽ thực hiện một buổi thuyết trình giới thiệu sản phẩm cho khách hàng tại phòng 500 vào thứ Hai tuần tới).\n- 'Deliver a product demonstration' (thực hiện buổi thuyết trình thử nghiệm sản phẩm) đồng nghĩa với 'Give a presentation'.\n- Phương án đúng: (D) Thực hiện một bài thuyết trình."
    },

    # -------------------------------------------------------------------------
    # Group 6: 158-161 (test1-p7-g158_161)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q158",
        "group_id": "test1-p7-g158_161",
        "part": 7,
        "question_number": 158,
        "question_type_tag": "detail_lookup",
        "question_text": "At what time will the executive board meeting begin?",
        "options": {
            "A": "2:00 P.M.",
            "B": "2:15 P.M.",
            "C": "2:30 P.M.",
            "D": "3:00 P.M."
        },
        "correct_answer": "C",
        "evidence_quote": "I forgot you were going to the executive board meeting.",
        "paraphrase_pair": {
            "original": "different meeting at 2:30... executive board meeting",
            "paraphrased": "executive board meeting begin at 2:30 P.M."
        },
        "explanation_vi": "Phân tích câu hỏi: Cuộc họp ban điều hành (executive board meeting) sẽ bắt đầu lúc mấy giờ?\n- Dẫn chứng trong bài:\n  + Stef Goldberg (11:35 A.M.): '...I need to be at a different meeting at 2:30.'\n  + Ella Glatt (11:36 A.M.): 'Oh, right. I forgot you were going to the executive board meeting.'\n- Kết hợp 2 tin nhắn: Cuộc họp mà Stef phải dự lúc 2:30 chính là cuộc họp ban điều hành.\n- Phương án đúng: (C) 2:30 P.M.\n- Bẫy đề thi: (A) 2:00 P.M. là giờ bắt đầu cuộc họp phòng marketing (marketing meeting)."
    },
    {
        "id": "test1-q159",
        "group_id": "test1-p7-g158_161",
        "part": 7,
        "question_number": 159,
        "question_type_tag": "inference",
        "question_text": "In what area does Mr. Iverman most likely work?",
        "options": {
            "A": "Marketing",
            "B": "Finance",
            "C": "Advertising",
            "D": "Executive management"
        },
        "correct_answer": "B",
        "evidence_quote": "The quarterly reports just came in, and Daniel, Stef, and I need to review them by the end of the day.",
        "paraphrase_pair": {
            "original": "finance department... Daniel, Stef, and I",
            "paraphrased": "work in Finance"
        },
        "explanation_vi": "Phân tích câu hỏi: Ông Iverman nhiều khả năng làm việc ở bộ phận nào?\n- Dẫn chứng trong bài:\n  + Ella Glatt (11:34 A.M.): 'whether anyone from the finance team could come...'\n  + Ella Glatt (11:37 A.M.): 'someone from the finance department there...'\n  + Bill Iverman (11:38 A.M.): 'The quarterly reports just came in, and Daniel, Stef, and I need to review them by the end of the day.' (Báo cáo quý vừa gửi tới và Daniel, Stef cùng tôi cần phải xem xét xong trước cuối ngày).\n- Suy luận logic: Bill Iverman cùng nhóm xử lý báo cáo tài chính quý với Daniel và Stef (thuộc finance team).\n- Phương án đúng: (B) Tài chính (Finance)."
    },
    {
        "id": "test1-q160",
        "group_id": "test1-p7-g158_161",
        "part": 7,
        "question_number": 160,
        "question_type_tag": "detail_lookup",
        "question_text": "Why does Ms. Glatt want a colleague to attend a meeting?",
        "options": {
            "A": "To summarize a previous meeting",
            "B": "To explain a promotional campaign",
            "C": "To provide information about a budget",
            "D": "To review recently approved documents"
        },
        "correct_answer": "C",
        "evidence_quote": "We just need one of you to clarify a few quick points about the budget for the next advertising campaign.",
        "paraphrase_pair": {
            "original": "clarify a few quick points about the budget",
            "paraphrased": "provide information about a budget"
        },
        "explanation_vi": "Phân tích câu hỏi: Tại sao cô Glatt muốn một đồng nghiệp đến dự cuộc họp?\n- Dẫn chứng trong bài: Tin nhắn cuối của Ella Glatt (11:43 A.M.): 'We just need one of you to clarify a few quick points about the budget for the next advertising campaign.' (Chúng tôi chỉ cần một người trong các bạn làm rõ vài điểm nhanh về ngân sách cho chiến dịch quảng cáo sắp tới).\n- 'Clarify points about the budget' đồng nghĩa với 'provide information about a budget'.\n- Phương án đúng: (C) Để cung cấp thông tin liên quan đến ngân sách."
    },
    {
        "id": "test1-q161",
        "group_id": "test1-p7-g158_161",
        "part": 7,
        "question_number": 161,
        "question_type_tag": "intent",
        "question_text": "At 11:43 A.M., what does Ms. Glatt most likely mean when she writes, \"Sounds great\"?",
        "options": {
            "A": "She accepts Mr. Seidal's offer.",
            "B": "She agrees that Mr. Iverman should attend the meeting at 3:00 P.M.",
            "C": "She is pleased with the proposed budget.",
            "D": "She is happy that a project has been completed."
        },
        "correct_answer": "A",
        "evidence_quote": "That's true! But I could come from 2:00 to 2:15. That's all I can commit to.",
        "paraphrase_pair": {
            "original": "I could come from 2:00 to 2:15... / Sounds great.",
            "paraphrased": "accepts Mr. Seidal's offer"
        },
        "explanation_vi": "Phân tích câu hỏi: Lúc 11:43 A.M., cô Glatt có ý gì khi viết 'Sounds great'?\n- Ngữ cảnh: Daniel Seidal đề xuất: 'But I could come from 2:00 to 2:15. That's all I can commit to.' (Tôi có thể ghé qua từ 2:00 đến 2:15. Đó là khoảng thời gian duy nhất tôi có thể dành ra được).\n- Khi cô Glatt đáp 'Sounds great', cô đồng ý và chấp nhận đề nghị tham gia 15 phút đó của ông Seidal.\n- Phương án đúng: (A) Cô ấy chấp nhận lời đề nghị của ông Seidal."
    },

    # -------------------------------------------------------------------------
    # Group 7: 162-165 (test1-p7-g162_165)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q162",
        "group_id": "test1-p7-g162_165",
        "part": 7,
        "question_number": 162,
        "question_type_tag": "detail_lookup",
        "question_text": "What does Ms. McFarland mention about Mr. Wilkins?",
        "options": {
            "A": "He informed her of a job opening.",
            "B": "He will require a professional reference.",
            "C": "He would make a good business partner.",
            "D": "He is considering resigning from his position."
        },
        "correct_answer": "A",
        "evidence_quote": "My friend Josiah Wilkins told me that you are seeking a project coordinator for your company.",
        "paraphrase_pair": {
            "original": "told me that you are seeking a project coordinator",
            "paraphrased": "informed her of a job opening"
        },
        "explanation_vi": "Phân tích câu hỏi: Cô McFarland đề cập điều gì về ông Wilkins?\n- Dẫn chứng trong bài: Câu mở đầu thư 'My friend Josiah Wilkins told me that you are seeking a project coordinator for your company.' (Bạn tôi là Josiah Wilkins đã cho tôi biết rằng ông đang tìm kiếm một điều phối viên dự án cho công ty).\n- Phương án đúng: (A) Ông ấy đã thông báo cho cô về một vị trí tuyển dụng còn trống (informed her of a job opening)."
    },
    {
        "id": "test1-q163",
        "group_id": "test1-p7-g162_165",
        "part": 7,
        "question_number": 163,
        "question_type_tag": "vocabulary",
        "question_text": "The word \"convey\" in paragraph 1, line 5, is closest in meaning to",
        "options": {
            "A": "transport",
            "B": "communicate",
            "C": "recommend",
            "D": "adapt"
        },
        "correct_answer": "B",
        "evidence_quote": "I can convey expectations clearly to team members involved in each phase of a project.",
        "paraphrase_pair": {
            "original": "convey expectations clearly",
            "paraphrased": "communicate expectations clearly"
        },
        "explanation_vi": "Phân tích câu hỏi từ vựng trong ngữ cảnh: Từ 'convey' trong đoạn 1 gần nghĩa nhất với từ nào?\n- Câu văn gốc: '...and I can convey expectations clearly to team members involved in each phase of a project.' (và tôi có thể truyền đạt các kỳ vọng một cách rõ ràng tới các thành viên trong nhóm).\n- 'Convey information/expectations' nghĩa là truyền đạt, truyền tải thông tin, đồng nghĩa với 'communicate'.\n- Phương án đúng: (B) communicate.\n- Bẫy từ vựng: (A) transport (chuyên chở - nghĩa gốc cơ học của convey như băng chuyền conveyor, nhưng trong giao tiếp thì mang nghĩa truyền đạt)."
    },
    {
        "id": "test1-q164",
        "group_id": "test1-p7-g162_165",
        "part": 7,
        "question_number": 164,
        "question_type_tag": "inference",
        "question_text": "Why does Ms. McFarland want to leave her current position?",
        "options": {
            "A": "She wants a higher salary for her efforts.",
            "B": "She wants to work with a more experienced team.",
            "C": "She wants more opportunities for advancement.",
            "D": "She wants a role that inspires her more."
        },
        "correct_answer": "D",
        "evidence_quote": "While I enjoy the kind of work I do, it has become clear to me that I need motivation from a strong mission.",
        "paraphrase_pair": {
            "original": "I need motivation from a strong mission",
            "paraphrased": "wants a role that inspires her more"
        },
        "explanation_vi": "Phân tích câu hỏi: Tại sao cô McFarland lại muốn rời bỏ vị trí công việc hiện tại?\n- Dẫn chứng trong bài: Đoạn 2 ghi: 'While I enjoy the kind of work I do, it has become clear to me that I need motivation from a strong mission. The goal of your company to create sustainable housing projects is something that I strongly support...'\n- Cần động lực từ một sứ mệnh lớn lao ('motivation from a strong mission') đồng nghĩa với muốn một vai trò mang lại nhiều cảm hứng hơn ('a role that inspires her more').\n- Phương án đúng: (D) Cô muốn một công việc truyền cho cô nhiều cảm hứng hơn."
    },
    {
        "id": "test1-q165",
        "group_id": "test1-p7-g162_165",
        "part": 7,
        "question_number": 165,
        "question_type_tag": "detail_lookup",
        "question_text": "Why does Ms. McFarland mention her travels?",
        "options": {
            "A": "To request a placement in a particular country",
            "B": "To discuss how she came to acquire strategic industry contacts",
            "C": "To explain how she became aware of certain world issues",
            "D": "To emphasize her experience with people of different backgrounds"
        },
        "correct_answer": "D",
        "evidence_quote": "This seems particularly relevant to mention, as I am comfortable leading geographically and culturally diverse teams.",
        "paraphrase_pair": {
            "original": "comfortable leading geographically and culturally diverse teams",
            "paraphrased": "experience with people of different backgrounds"
        },
        "explanation_vi": "Phân tích câu hỏi: Tại sao cô McFarland đề cập đến những chuyến đi ra nước ngoài của mình?\n- Dẫn chứng trong bài: Đoạn 3: 'Through my work and volunteer activities, I have spent many months abroad in various countries... This seems particularly relevant to mention, as I am comfortable leading geographically and culturally diverse teams.'\n- 'Culturally diverse teams' (các đội nhóm đa dạng về văn hóa và địa lý) chính là 'people of different backgrounds' (những người có xuất thân/nền tảng khác nhau).\n- Phương án đúng: (D) Để nhấn mạnh kinh nghiệm làm việc với những người có xuất thân đa dạng."
    },

    # -------------------------------------------------------------------------
    # Group 8: 166-168 (test1-p7-g166_168)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q166",
        "group_id": "test1-p7-g166_168",
        "part": 7,
        "question_number": 166,
        "question_type_tag": "detail_lookup",
        "question_text": "What does Trexdale Supply make?",
        "options": {
            "A": "Medical supplies",
            "B": "Farming equipment",
            "C": "Cabinets and furniture",
            "D": "Glass laboratory equipment"
        },
        "correct_answer": "C",
        "evidence_quote": "Trexdale Supply specializes in designing, producing, and installing furniture for all types of scientific laboratories. We provide a range of fully assembled cabinets, workstations, benches, and more",
        "paraphrase_pair": {
            "original": "furniture... cabinets, workstations, benches",
            "paraphrased": "Cabinets and furniture"
        },
        "explanation_vi": "Phân tích câu hỏi: Công ty Trexdale Supply sản xuất mặt hàng gì?\n- Dẫn chứng trong bài: Đoạn 1: 'Trexdale Supply specializes in designing, producing, and installing furniture for all types of scientific laboratories. We provide a range of fully assembled cabinets, workstations, benches...'\n- Phương án đúng: (C) Tủ và đồ nội thất (Cabinets and furniture)."
    },
    {
        "id": "test1-q167",
        "group_id": "test1-p7-g166_168",
        "part": 7,
        "question_number": 167,
        "question_type_tag": "detail_lookup",
        "question_text": "What did Trexdale Supply do in a recent project?",
        "options": {
            "A": "It reorganized a client's laboratory.",
            "B": "It converted its vehicles to use biofuels.",
            "C": "It expanded staffing at its production facility.",
            "D": "It helped a client organize a trade show."
        },
        "correct_answer": "A",
        "evidence_quote": "changing the layout of a research laboratory to maximize available space",
        "paraphrase_pair": {
            "original": "changing the layout of a research laboratory",
            "paraphrased": "reorganized a client's laboratory"
        },
        "explanation_vi": "Phân tích câu hỏi: Công ty Trexdale Supply đã làm gì trong một dự án gần đây?\n- Dẫn chứng trong bài: Đoạn 2: 'Recently, for example, we were chosen by a major producer of biofuels to provide expert help in changing the layout of a research laboratory to maximize available space.' (Gần đây, chúng tôi được chọn để hỗ trợ thay đổi bố cục sắp xếp của một phòng thí nghiệm nghiên cứu nhằm tối đa hóa diện tích).\n- 'Changing the layout of a laboratory' được diễn đạt lại thành 'reorganized a client's laboratory'.\n- Phương án đúng: (A) Tái cơ cấu / sắp xếp lại bố cục phòng thí nghiệm cho khách hàng."
    },
    {
        "id": "test1-q168",
        "group_id": "test1-p7-g166_168",
        "part": 7,
        "question_number": 168,
        "question_type_tag": "detail_lookup",
        "question_text": "What method of communicating with Trexdale Supply is mentioned?",
        "options": {
            "A": "By e-mail",
            "B": "By phone",
            "C": "By instant message",
            "D": "By an online form"
        },
        "correct_answer": "D",
        "evidence_quote": "fill out an interest form to contact one of our consultants about your next project.",
        "paraphrase_pair": {
            "original": "fill out an interest form to contact one of our consultants",
            "paraphrased": "By an online form"
        },
        "explanation_vi": "Phân tích câu hỏi: Phương thức liên hệ nào với Trexdale Supply được nhắc đến trong bài?\n- Dẫn chứng trong bài: Câu cuối đoạn 3: 'Please visit the \"Lab Planning\" section of this Web site... There, you can fill out an interest form to contact one of our consultants about your next project.' (Bạn có thể điền vào một biểu mẫu quan tâm để liên hệ với chuyên viên tư vấn).\n- Phương án đúng: (D) Bằng biểu mẫu trực tuyến (By an online form)."
    },

    # -------------------------------------------------------------------------
    # Group 9: 169-171 (test1-p7-g169_171)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q169",
        "group_id": "test1-p7-g169_171",
        "part": 7,
        "question_number": 169,
        "question_type_tag": "inference",
        "question_text": "What work experience would best qualify a candidate for the position?",
        "options": {
            "A": "Cook",
            "B": "Cashier",
            "C": "Interior designer",
            "D": "Event planner"
        },
        "correct_answer": "A",
        "evidence_quote": "candidates must have a Professional Food Handler certificate.",
        "paraphrase_pair": {
            "original": "prepare simple recipes... working with food, candidates must have a Professional Food Handler certificate",
            "paraphrased": "Cook"
        },
        "explanation_vi": "Phân tích câu hỏi: Kinh nghiệm làm việc nào sẽ phù hợp nhất cho ứng viên ứng tuyển vị trí này?\n- Dẫn chứng trong bài: 'For some products, you will be required to prepare simple recipes... Because many of the demonstrations require working with food, candidates must have a Professional Food Handler certificate.' (Chuẩn bị các công thức nấu ăn đơn giản, làm việc với thực phẩm và cần có chứng chỉ an toàn vệ sinh thực phẩm).\n- Suy luận logic: Kinh nghiệm làm đầu bếp (Cook) là phù hợp nhất với các yêu cầu này.\n- Phương án đúng: (A) Đầu bếp (Cook)."
    },
    {
        "id": "test1-q170",
        "group_id": "test1-p7-g169_171",
        "part": 7,
        "question_number": 170,
        "question_type_tag": "detail_lookup",
        "question_text": "According to the advertisement, what should people interested in applying do next?",
        "options": {
            "A": "Respond to a survey",
            "B": "Arrange for an interview",
            "C": "Submit a recording",
            "D": "Provide references"
        },
        "correct_answer": "C",
        "evidence_quote": "upload a video of no more than one minute in length telling us why you would be a successful product demonstrator",
        "paraphrase_pair": {
            "original": "upload a video of no more than one minute in length",
            "paraphrased": "Submit a recording"
        },
        "explanation_vi": "Phân tích câu hỏi: Theo mẩu quảng cáo, những người quan tâm ứng tuyển cần làm bước gì tiếp theo?\n- Dẫn chứng trong bài: 'To apply, upload a video of no more than one minute in length telling us why you would be a successful product demonstrator at www.bbdstaffing.com/applications.' (Để ứng tuyển, tải lên một video dài không quá 1 phút).\n- 'Upload a video' (tải lên một video clip) được diễn đạt lại thành 'Submit a recording' (nộp một bản ghi hình/ghi âm).\n- Phương án đúng: (C) Nộp một bản ghi hình (Submit a recording)."
    },
    {
        "id": "test1-q171",
        "group_id": "test1-p7-g169_171",
        "part": 7,
        "question_number": 171,
        "question_type_tag": "sentence_insertion",
        "question_text": "In which of the positions marked [1], [2], [3], and [4] does the following sentence best belong?\n\"Many of the world's best-known brands rely on our product demonstrators to generate positive impressions of their products.\"",
        "options": {
            "A": "[1]",
            "B": "[2]",
            "C": "[3]",
            "D": "[4]"
        },
        "correct_answer": "C",
        "evidence_quote": "BBD Staffing is seeking to hire in-store product demonstrators to promote our clients' merchandise to shoppers.",
        "paraphrase_pair": {
            "original": "promote our clients' merchandise... Many of the world's best-known brands rely on our product demonstrators",
            "paraphrased": "sentence placement [3]"
        },
        "explanation_vi": "Phân tích câu hỏi chèn câu (Sentence Insertion): Câu cần chèn: 'Many of the world's best-known brands rely on our product demonstrators to generate positive impressions of their products.' (Nhiều thương hiệu nổi tiếng nhất thế giới tin tưởng vào đội ngũ người giới thiệu sản phẩm của chúng tôi để tạo ấn tượng tích cực về sản phẩm của họ).\n- Xét vị trí [3]: Câu đứng trước đề cập đến việc BBD Staffing tuyển dụng người giới thiệu sản phẩm để quảng bá hàng hóa của khách hàng ('promote our clients' merchandise to shoppers'). Câu cần chèn phát triển cụ thể 'clients' này chính là 'Many of the world's best-known brands'. Tiếp đó, câu sau nói về vai trò của ứng viên khi gia nhập đội ngũ ('As a member of our team...'). Mạch văn rất chặt chẽ và tự nhiên.\n- Phương án đúng: (C) Vị trí [3]."
    },

    # -------------------------------------------------------------------------
    # Group 10: 172-175 (test1-p7-g172_175)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q172",
        "group_id": "test1-p7-g172_175",
        "part": 7,
        "question_number": 172,
        "question_type_tag": "intent",
        "question_text": "What is the purpose of the article?",
        "options": {
            "A": "To promote a technology show",
            "B": "To introduce a product",
            "C": "To interview smartphone users",
            "D": "To announce a recall of a device"
        },
        "correct_answer": "B",
        "evidence_quote": "Gorman Mobile unveiled its newest smartphone to an eager reception at the annual Technobrit exhibition yesterday.",
        "paraphrase_pair": {
            "original": "unveiled its newest smartphone... The Gorman Pro Phone 4",
            "paraphrased": "introduce a product"
        },
        "explanation_vi": "Phân tích câu hỏi: Mục đích chính của bài viết là gì?\n- Dẫn chứng trong bài: Tiêu đề 'Gorman Unveils Newest Smartphone Model' và câu mở đầu: 'Gorman Mobile unveiled its newest smartphone to an eager reception... The Gorman Pro Phone 4, which includes 512 GB of storage...'\n- Giới thiệu một mẫu điện thoại thông minh mới chính là 'introduce a product'.\n- Phương án đúng: (B) Giới thiệu một sản phẩm mới (To introduce a product)."
    },
    {
        "id": "test1-q173",
        "group_id": "test1-p7-g172_175",
        "part": 7,
        "question_number": 173,
        "question_type_tag": "detail_lookup",
        "question_text": "How much do the Gorman Pro Phone 4 wireless headphones cost?",
        "options": {
            "A": "£39",
            "B": "£59",
            "C": "£79",
            "D": "£100"
        },
        "correct_answer": "C",
        "evidence_quote": "Add-ons, such as the stylus pen, protective case, and wireless headphones, cost an additional £39, £59, and £79, respectively.",
        "paraphrase_pair": {
            "original": "wireless headphones, cost an additional... £79, respectively",
            "paraphrased": "cost £79"
        },
        "explanation_vi": "Phân tích câu hỏi: Tai nghe không dây của điện thoại Gorman Pro Phone 4 có giá bao nhiêu?\n- Dẫn chứng trong bài: Đoạn 2 liệt kê tương ứng ('respectively'):\n  + stylus pen: £39\n  + protective case: £59\n  + wireless headphones: £79\n- Đối chiếu vị trí thứ 3 là 'wireless headphones' tương ứng với mức giá £79.\n- Phương án đúng: (C) £79."
    },
    {
        "id": "test1-q174",
        "group_id": "test1-p7-g172_175",
        "part": 7,
        "question_number": 174,
        "question_type_tag": "detail_lookup",
        "question_text": "What does the Pro Phone 4 have in common with prior models?",
        "options": {
            "A": "The screen size",
            "B": "The camera resolution",
            "C": "The price",
            "D": "The charger"
        },
        "correct_answer": "D",
        "evidence_quote": "One similarity that the Pro Phone 4 has with previous models is the charger.",
        "paraphrase_pair": {
            "original": "One similarity that the Pro Phone 4 has with previous models is the charger",
            "paraphrased": "in common with prior models: The charger"
        },
        "explanation_vi": "Phân tích câu hỏi: Điện thoại Pro Phone 4 có điểm gì chung với các mẫu đời trước?\n- Dẫn chứng trong bài: Đoạn cuối: 'One similarity that the Pro Phone 4 has with previous models is the charger. Going against the trend of competing wireless companies, Gorman is instead focusing on convenience. We want to afford our customers the ability to reuse elements of the other Gorman devices they've already purchased...'\n- 'Similarity with previous models' (điểm tương đồng với mẫu trước) = 'have in common with prior models'.\n- Phương án đúng: (D) Củ sạc / bộ sạc (The charger)."
    },
    {
        "id": "test1-q175",
        "group_id": "test1-p7-g172_175",
        "part": 7,
        "question_number": 175,
        "question_type_tag": "sentence_insertion",
        "question_text": "In which of the positions marked [1], [2], [3], and [4] does the following sentence best belong?\n\"These upgrades do come at a cost.\"",
        "options": {
            "A": "[1]",
            "B": "[2]",
            "C": "[3]",
            "D": "[4]"
        },
        "correct_answer": "A",
        "evidence_quote": "The £999 starting price is £100 more than that of the previous model.",
        "paraphrase_pair": {
            "original": "upgrades... come at a cost. The £999 starting price is £100 more",
            "paraphrased": "sentence placement [1]"
        },
        "explanation_vi": "Phân tích câu hỏi chèn câu: Câu cần chèn: 'These upgrades do come at a cost.' (Tuy nhiên, những nâng cấp này cũng đi kèm với một mức giá/chi phí đáng kể).\n- Xét vị trí [1]: Đoạn 1 vừa liệt kê hàng loạt nâng cấp vượt trội ('larger screen, ultrawide camera lens, 8K-resolution filming capability'). Ngay sau vị trí [1] là câu giải thích về giá thành: 'The £999 starting price is £100 more than that of the previous model.' (Giá khởi điểm £999 đắt hơn đời trước £100). Do đó câu nối 'These upgrades do come at a cost' đặt ở [1] là hoàn hảo về logic chuyển ý.\n- Phương án đúng: (A) Vị trí [1]."
    },

    # -------------------------------------------------------------------------
    # Group 11: 176-180 (test1-p7-g176_180)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q176",
        "group_id": "test1-p7-g176_180",
        "part": 7,
        "question_number": 176,
        "question_type_tag": "inference",
        "question_text": "What does Ms. Xi's request indicate about the company?",
        "options": {
            "A": "It provides mobile phones to some employees.",
            "B": "Its employees value confidentiality.",
            "C": "It has recently changed its phone system.",
            "D": "It offers technology training to employees."
        },
        "correct_answer": "C",
        "evidence_quote": "Is it possible to remove the new layers of security on my voice mail in the new phone system?",
        "paraphrase_pair": {
            "original": "in the new phone system",
            "paraphrased": "recently changed its phone system"
        },
        "explanation_vi": "Phân tích câu hỏi liên kết: Yêu cầu của cô Xi cho thấy điều gì về công ty?\n- Dẫn chứng trong văn bản:\n  + Trong Work Order: 'Is it possible to remove the new layers of security on my voice mail in the new phone system?'\n  + Trong Email: 'This is in reference to your work order 7549 related to the new phone system.'\n- Cụm từ 'in the new phone system' (trong hệ thống điện thoại mới) ngụ ý rằng công ty vừa mới thay đổi/nâng cấp hệ thống điện thoại gần đây.\n- Phương án đúng: (C) Công ty gần đây đã thay đổi hệ thống điện thoại (recently changed its phone system)."
    },
    {
        "id": "test1-q177",
        "group_id": "test1-p7-g176_180",
        "part": 7,
        "question_number": 177,
        "question_type_tag": "vocabulary",
        "question_text": "In the e-mail, the word \"regular\" in paragraph 1, line 6, is closest in meaning to",
        "options": {
            "A": "periodic",
            "B": "orderly",
            "C": "customary",
            "D": "legitimate"
        },
        "correct_answer": "A",
        "evidence_quote": "I can update the security settings so that you do not have to reset the password on a regular basis.",
        "paraphrase_pair": {
            "original": "on a regular basis",
            "paraphrased": "periodic"
        },
        "explanation_vi": "Phân tích từ vựng trong ngữ cảnh: Từ 'regular' trong cụm 'on a regular basis' có nghĩa là gì?\n- Câu gốc: 'I can update the security settings so that you do not have to reset the password on a regular basis.' (Tôi có thể cập nhật cài đặt bảo mật để bạn không phải đặt lại mật khẩu theo định kỳ thường xuyên nữa).\n- 'On a regular basis' = định kỳ, lặp đi lặp lại theo chu kỳ thời gian = 'periodic'.\n- Phương án đúng: (A) periodic (định kỳ)."
    },
    {
        "id": "test1-q178",
        "group_id": "test1-p7-g176_180",
        "part": 7,
        "question_number": 178,
        "question_type_tag": "detail_lookup",
        "question_text": "Where did Mr. Arnold learn about the details of Ms. Xi's request?",
        "options": {
            "A": "In a weekly managers' meeting",
            "B": "In a work order",
            "C": "In a phone call",
            "D": "In a personal voice mail"
        },
        "correct_answer": "B",
        "evidence_quote": "This is in reference to your work order 7549 related to the new phone system.",
        "paraphrase_pair": {
            "original": "reference to your work order 7549",
            "paraphrased": "In a work order"
        },
        "explanation_vi": "Phân tích câu hỏi: Ông Arnold đã nắm được chi tiết yêu cầu của cô Xi từ đâu?\n- Dẫn chứng trong văn bản: Trong Email gửi cô Xi, ông Arnold mở đầu: 'This is in reference to your work order 7549 related to the new phone system.' (Thư này liên quan đến phiếu yêu cầu công việc số 7549 của cô).\n- Phương án đúng: (B) Trong một phiếu yêu cầu công việc (In a work order)."
    },
    {
        "id": "test1-q179",
        "group_id": "test1-p7-g176_180",
        "part": 7,
        "question_number": 179,
        "question_type_tag": "inference",
        "question_text": "How does Mr. Arnold try to satisfy Ms. Xi's request?",
        "options": {
            "A": "By agreeing to everything Ms. Xi asked for",
            "B": "By resetting the password on Ms. Xi's phone",
            "C": "By referring the matter to another technician",
            "D": "By proposing to fulfill only part of Ms. Xi's request"
        },
        "correct_answer": "D",
        "evidence_quote": "company policy allows me to change the settings for employees who do not work with confidential material. I can update the security settings so that you do not have to reset the password on a regular basis.",
        "paraphrase_pair": {
            "original": "require password... but do not have to reset on regular basis",
            "paraphrased": "proposing to fulfill only part of Ms. Xi's request"
        },
        "explanation_vi": "Phân tích câu hỏi: Ông Arnold cố gắng đáp ứng yêu cầu của cô Xi bằng cách nào?\n- Dẫn chứng so sánh:\n  + Cô Xi xin: (1) không phải dùng mật khẩu VÀ (2) không phải đổi mật khẩu hàng tháng.\n  + Ông Arnold trả lời: Hệ thống bắt buộc vẫn phải có mật khẩu ('system does require you to have a password'), nhưng ông có thể điều chỉnh để cô không phải đổi mật khẩu định kỳ nữa ('password never expires').\n- Như vậy ông chỉ đáp ứng được MỘT PHẦN yêu cầu của cô Xi.\n- Phương án đúng: (D) Bằng cách đề xuất thực hiện một phần yêu cầu của cô Xi (fulfill only part of Ms. Xi's request)."
    },
    {
        "id": "test1-q180",
        "group_id": "test1-p7-g176_180",
        "part": 7,
        "question_number": 180,
        "question_type_tag": "detail_lookup",
        "question_text": "What does Arnold ask Ms. Xi to do?",
        "options": {
            "A": "Make the needed changes to her voice-mail system",
            "B": "Attend training about the new voice-mail system",
            "C": "Confirm that she wants him to change her voice-mail system",
            "D": "Provide a clear description of the problem with her voice-mail system"
        },
        "correct_answer": "C",
        "evidence_quote": "If you still feel comfortable with that level of risk, let me know, and I will change the settings so that your password never expires.",
        "paraphrase_pair": {
            "original": "If you still feel comfortable with that level of risk, let me know",
            "paraphrased": "Confirm that she wants him to change her voice-mail system"
        },
        "explanation_vi": "Phân tích câu hỏi: Ông Arnold yêu cầu cô Xi làm điều gì?\n- Dẫn chứng trong bài: Câu cuối email: 'If you still feel comfortable with that level of risk, let me know, and I will change the settings so that your password never expires.' (Nếu cô vẫn cảm thấy an tâm với mức độ rủi ro đó, hãy cho tôi biết và tôi sẽ thay đổi cài đặt để mật khẩu của cô không bao giờ hết hạn).\n- 'Let me know' (báo lại cho tôi biết) chính là yêu cầu xác nhận ('Confirm that she wants him to change...').\n- Phương án đúng: (C) Xác nhận rằng cô vẫn muốn ông thay đổi cài đặt hệ thống hộp thư thoại."
    },

    # -------------------------------------------------------------------------
    # Group 12: 181-185 (test1-p7-g181_185)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q181",
        "group_id": "test1-p7-g181_185",
        "part": 7,
        "question_number": 181,
        "question_type_tag": "inference",
        "question_text": "In the e-mail, what is suggested about Mr. Merson?",
        "options": {
            "A": "He coordinates a game development team.",
            "B": "He is convinced that Titan Adventure is overpriced.",
            "C": "He is a new employee at Rimerko Games.",
            "D": "He will leave on a business trip on October 10."
        },
        "correct_answer": "A",
        "evidence_quote": "Project Manager, Rimerko Games",
        "paraphrase_pair": {
            "original": "Project Manager, Rimerko Games / The team was hoping to have one last rendering",
            "paraphrased": "coordinates a game development team"
        },
        "explanation_vi": "Phân tích câu hỏi: Trong bức email, điều gì được gợi ý về ông Merson?\n- Dẫn chứng trong bài: Chữ ký email ghi 'Cliff Merson, Project Manager, Rimerko Games' và trong thư ông viết 'The team was hoping to have one last rendering... All other aspects of the game are on schedule.' (Nhóm phát triển hy vọng có bản dựng ánh sáng cuối cùng trước ngày 10/10... Tất cả các khía cạnh khác của trò chơi đều đúng tiến độ).\n- Chức vụ Giám đốc dự án điều phối tiến độ của nhóm làm game = 'coordinates a game development team'.\n- Phương án đúng: (A) Ông ấy điều phối một nhóm phát triển trò chơi."
    },
    {
        "id": "test1-q182",
        "group_id": "test1-p7-g181_185",
        "part": 7,
        "question_number": 182,
        "question_type_tag": "detail_lookup",
        "question_text": "In the review, what is indicated about Neptune's Voyage?",
        "options": {
            "A": "It is a major competitor of Titan Adventure.",
            "B": "It features an open-world format.",
            "C": "It is the first video game in a series.",
            "D": "It is Rimerko's most challenging game."
        },
        "correct_answer": "B",
        "evidence_quote": "Though open-world formats have been widespread in recent years, Neptune's Voyage brings something new to the format.",
        "paraphrase_pair": {
            "original": "Neptune's Voyage brings something new to the format [open-world format]",
            "paraphrased": "features an open-world format"
        },
        "explanation_vi": "Phân tích câu hỏi: Trong bài đánh giá (review), điều gì được chỉ ra về tựa game Neptune's Voyage?\n- Dẫn chứng trong bài: Đoạn 1 của bài đánh giá: 'Though open-world formats have been widespread in recent years, Neptune's Voyage brings something new to the format.' (Mặc dù định dạng thế giới mở đã rất phổ biến... Neptune's Voyage mang lại điều mới mẻ cho định dạng này).\n- Phương án đúng: (B) Trò chơi có định dạng thế giới mở (open-world format)."
    },
    {
        "id": "test1-q183",
        "group_id": "test1-p7-g181_185",
        "part": 7,
        "question_number": 183,
        "question_type_tag": "cross_text_inference",
        "question_text": "What can be concluded about Ms. Hanshu?",
        "options": {
            "A": "She wrote the script for Neptune's Voyage.",
            "B": "She successfully addressed Mr. Merson's concern.",
            "C": "She won an award for game design.",
            "D": "She is a project manager."
        },
        "correct_answer": "B",
        "evidence_quote": "This newest version also corrects the green and blue image rendering that was sometimes a problem in earlier installments of Titan Adventure.",
        "paraphrase_pair": {
            "original": "take charge of lighting... found solution / corrects the green and blue image rendering",
            "paraphrased": "successfully addressed Mr. Merson's concern"
        },
        "explanation_vi": "Phân tích câu hỏi liên kết 2 văn bản (Cross-text Inference):\n- Văn bản 1 (Email): Ông Merson bày tỏ lo lắng với bà Hanshu về lỗi ánh sáng tông xanh lá và xanh dương ('getting the reflections and lighting in green and blue areas correct has been a particular challenge... You said you would take charge of this').\n- Văn bản 2 (Review): Nhà phê bình khen ngợi: 'This newest version also corrects the green and blue image rendering that was sometimes a problem in earlier installments of Titan Adventure.' (Phiên bản mới nhất này cũng đã khắc phục lỗi dựng hình ảnh màu xanh lá và xanh lam từng gặp ở các phần trước).\n- Kết luận: Bà Hanshu đã giải quyết thành công vấn đề mà ông Merson lo lắng.\n- Phương án đúng: (B) Cô ấy đã giải quyết thành công mối bận tâm của ông Merson."
    },
    {
        "id": "test1-q184",
        "group_id": "test1-p7-g181_185",
        "part": 7,
        "question_number": 184,
        "question_type_tag": "detail_lookup",
        "question_text": "What does Mr. Weber find exciting about Neptune's Voyage?",
        "options": {
            "A": "It has players act in the role of Neptune.",
            "B": "It uses lighting to show players where to navigate.",
            "C": "It introduces a completely new set of characters.",
            "D": "It lets players explore new features without guidance."
        },
        "correct_answer": "D",
        "evidence_quote": "By stripping down instructional guides, the game gives users the opportunity to discover new areas and devices.",
        "paraphrase_pair": {
            "original": "stripping down instructional guides... discover new areas and devices",
            "paraphrased": "explore new features without guidance"
        },
        "explanation_vi": "Phân tích câu hỏi: Ông Weber cảm thấy điều gì thú vị về Neptune's Voyage?\n- Dẫn chứng trong bài: Đoạn 1 của bài đánh giá: 'By stripping down instructional guides, the game gives users the opportunity to discover new areas and devices.' (Bằng cách lược bỏ các chỉ dẫn hướng dẫn rườm rà, trò chơi mang lại cho người chơi cơ hội tự mình khám phá các khu vực và thiết bị mới).\n- 'Stripping down instructional guides' = 'without guidance' (không cần hướng dẫn).\n- Phương án đúng: (D) Trò chơi cho phép người chơi tự do khám phá các tính năng mới mà không cần chỉ dẫn gò bó."
    },
    {
        "id": "test1-q185",
        "group_id": "test1-p7-g181_185",
        "part": 7,
        "question_number": 185,
        "question_type_tag": "detail_lookup",
        "question_text": "When will Neptune's Voyage be available?",
        "options": {
            "A": "On September 4",
            "B": "On October 10",
            "C": "On April 1",
            "D": "On May 5"
        },
        "correct_answer": "D",
        "evidence_quote": "Neptune's Voyage launches May 5 on Rimerko Clutch and PS5.",
        "paraphrase_pair": {
            "original": "launches May 5",
            "paraphrased": "available on May 5"
        },
        "explanation_vi": "Phân tích câu hỏi: Khi nào thì Neptune's Voyage sẽ chính thức phát hành / có mặt trên thị trường?\n- Dẫn chứng trong bài: Câu cuối bài review: 'Neptune's Voyage launches May 5 on Rimerko Clutch and PS5.' (Neptune's Voyage sẽ ra mắt vào ngày 5 tháng 5).\n- Phương án đúng: (D) Vào ngày 5 tháng 5 (On May 5)."
    },

    # -------------------------------------------------------------------------
    # Group 13: 186-190 (test1-p7-g186_190)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q186",
        "group_id": "test1-p7-g186_190",
        "part": 7,
        "question_number": 186,
        "question_type_tag": "detail_lookup",
        "question_text": "According to the schedule, who is Ms. Jones?",
        "options": {
            "A": "The advertising manager at a radio station",
            "B": "The host of a community news program",
            "C": "The music director at Wonder Ridge Radio",
            "D": "The host of a sports radio program"
        },
        "correct_answer": "C",
        "evidence_quote": "Host: Josie Jones (Wonder Ridge Radio Music Director)",
        "paraphrase_pair": {
            "original": "Wonder Ridge Radio Music Director",
            "paraphrased": "The music director at Wonder Ridge Radio"
        },
        "explanation_vi": "Phân tích câu hỏi: Theo lịch phát sóng, bà Jones là ai?\n- Dẫn chứng trong bài: Khung giờ 7 P.M.–10 P.M.: 'JOSIE'S JOINT - Host: Josie Jones (Wonder Ridge Radio Music Director)'.\n- Phương án đúng: (C) Giám đốc âm nhạc tại Đài phát thanh Wonder Ridge Radio."
    },
    {
        "id": "test1-q187",
        "group_id": "test1-p7-g186_190",
        "part": 7,
        "question_number": 187,
        "question_type_tag": "intent",
        "question_text": "What is the purpose of the e-mail?",
        "options": {
            "A": "To express praise for the radio station",
            "B": "To ask about job opportunities",
            "C": "To request more sports talk show programming",
            "D": "To inquire about the name of a song"
        },
        "correct_answer": "A",
        "evidence_quote": "Keep up the fantastic programming!",
        "paraphrase_pair": {
            "original": "blown away by incredible folk tracks... Keep up the fantastic programming!",
            "paraphrased": "express praise for the radio station"
        },
        "explanation_vi": "Phân tích câu hỏi: Mục đích chính của bức email của ông Eric Fabre là gì?\n- Dẫn chứng trong bài: Ông viết 'I was blown away by the incredible folk tracks Penny was playing. It made the rush-hour traffic completely bearable. Keep up the fantastic programming!' (Tôi hoàn toàn bị choáng ngợp bởi những bản nhạc dân gian tuyệt vời... Hãy tiếp tục duy trì những chương trình xuất sắc này nhé!).\n- Lời khen ngợi chương trình phát thanh = 'To express praise for the radio station'.\n- Phương án đúng: (A) Bày tỏ lời khen ngợi dành cho đài phát thanh."
    },
    {
        "id": "test1-q188",
        "group_id": "test1-p7-g186_190",
        "part": 7,
        "question_number": 188,
        "question_type_tag": "cross_text_inference",
        "question_text": "When did Mr. Fabre most likely first listen to Wonder Ridge Radio?",
        "options": {
            "A": "Between 6 A.M. and noon",
            "B": "Between noon and 4 P.M.",
            "C": "Between 4 P.M. and 7 P.M.",
            "D": "Between 7 P.M. and 10 P.M."
        },
        "correct_answer": "C",
        "evidence_quote": "driving home from work around 5:30 P.M.",
        "paraphrase_pair": {
            "original": "around 5:30 P.M. (Folk Frenzy)",
            "paraphrased": "Between 4 P.M. and 7 P.M."
        },
        "explanation_vi": "Phân tích câu hỏi liên kết văn bản:\n- Trong email, ông Fabre cho biết ông tình cờ nghe đài khi đang lái xe đi làm về vào khoảng 5:30 P.M. ('driving home from work around 5:30 P.M.').\n- Đối chiếu với Lịch phát sóng (Văn bản 1): Khung giờ 5:30 P.M. nằm trong khoảng '4 P.M.–7 P.M.: FOLK FRENZY (Host: Penny Ariza)'.\n- Phương án đúng: (C) Từ 4 giờ chiều đến 7 giờ tối (Between 4 P.M. and 7 P.M.)."
    },
    {
        "id": "test1-q189",
        "group_id": "test1-p7-g186_190",
        "part": 7,
        "question_number": 189,
        "question_type_tag": "detail_lookup",
        "question_text": "What does the job advertisement suggest applicants must have?",
        "options": {
            "A": "A willingness to travel",
            "B": "Familiarity with computers",
            "C": "A degree in communications",
            "D": "Extensive experience in the radio industry"
        },
        "correct_answer": "B",
        "evidence_quote": "demonstrated computer literacy and familiarity with social media",
        "paraphrase_pair": {
            "original": "demonstrated computer literacy",
            "paraphrased": "Familiarity with computers"
        },
        "explanation_vi": "Phân tích câu hỏi: Mẩu tin tuyển dụng gợi ý rằng các ứng viên bắt buộc phải có điều gì?\n- Dẫn chứng trong bài: Phần Requirements của tin tuyển dụng ghi: 'Requirements: High school diploma; demonstrated computer literacy and familiarity with social media...' (Bằng tốt nghiệp phổ thông, khả năng tin học thành thạo và quen thuộc với mạng xã hội).\n- 'Computer literacy' đồng nghĩa với 'Familiarity with computers'.\n- Phương án đúng: (B) Sự thành thạo về máy tính (Familiarity with computers).\n- Bẫy đề thi: (D) sai vì bài ghi rõ 'Previous radio industry experience is not required' (không yêu cầu kinh nghiệm trước đó trong ngành phát thanh)."
    },
    {
        "id": "test1-q190",
        "group_id": "test1-p7-g186_190",
        "part": 7,
        "question_number": 190,
        "question_type_tag": "cross_text_inference",
        "question_text": "What radio program will probably receive the most support from the programming assistant?",
        "options": {
            "A": "Coffee Break",
            "B": "Afternoon Jazz",
            "C": "Folk Frenzy",
            "D": "Josie's Joint"
        },
        "correct_answer": "A",
        "evidence_quote": "Conducting background research on interviewees",
        "paraphrase_pair": {
            "original": "research on interviewees + interviews with community members",
            "paraphrased": "Coffee Break"
        },
        "explanation_vi": "Phân tích câu hỏi liên kết 3 văn bản:\n- Tin tuyển dụng nêu trách nhiệm trọng tâm của trợ lý chương trình: 'Conducting background research on interviewees' (Tìm hiểu thông tin nền tảng về các khách mời phỏng vấn).\n- Đối chiếu với Lịch phát sóng: Chỉ có duy nhất chương trình 'Coffee Break' (6 A.M.–Noon) có nội dung 'interviews with community members' (phỏng vấn các thành viên cộng đồng), trong khi các chương trình khác là chương trình thuần phát nhạc (Jazz, Folk, Nhạc buổi tối).\n- Do đó, trợ lý chương trình sẽ hỗ trợ đắc lực nhất cho chương trình Coffee Break.\n- Phương án đúng: (A) Coffee Break."
    },

    # -------------------------------------------------------------------------
    # Group 14: 191-195 (test1-p7-g191_195)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q191",
        "group_id": "test1-p7-g191_195",
        "part": 7,
        "question_number": 191,
        "question_type_tag": "detail_lookup",
        "question_text": "What do the instructions indicate about records requests?",
        "options": {
            "A": "They can be made only on certain days.",
            "B": "They can be made only online.",
            "C": "They can be filed only by authorized personnel.",
            "D": "They can be filed only after a fee is paid."
        },
        "correct_answer": "B",
        "evidence_quote": "Currently, all requests must be made through the portal.",
        "paraphrase_pair": {
            "original": "all requests must be made through the portal",
            "paraphrased": "can be made only online"
        },
        "explanation_vi": "Phân tích câu hỏi: Bản hướng dẫn chỉ ra điều gì về việc yêu cầu cung cấp hồ sơ/tài liệu?\n- Dẫn chứng trong bài: Bước 1: 'Create an account in the Records Center Web portal. Currently, all requests must be made through the portal.' (Hiện tại, tất cả các yêu cầu bắt buộc phải thực hiện thông qua cổng thông tin trực tuyến).\n- 'Through the web portal' = 'online'.\n- Phương án đúng: (B) Các yêu cầu chỉ có thể được thực hiện trực tuyến (only online)."
    },
    {
        "id": "test1-q192",
        "group_id": "test1-p7-g191_195",
        "part": 7,
        "question_number": 192,
        "question_type_tag": "detail_lookup",
        "question_text": "According to the e-mail, how does Mr. Brandenberg plan to use some public information?",
        "options": {
            "A": "To add information to a Web portal",
            "B": "To help his company advise the city",
            "C": "To identify an accounting error",
            "D": "To learn how an agency is structured"
        },
        "correct_answer": "B",
        "evidence_quote": "which will inform our firm's current work advising the city on wastewater management.",
        "paraphrase_pair": {
            "original": "inform our firm's current work advising the city",
            "paraphrased": "help his company advise the city"
        },
        "explanation_vi": "Phân tích câu hỏi: Theo bức email, ông Brandenberg dự định sử dụng thông tin công khai này vào việc gì?\n- Dẫn chứng trong bài: Đoạn 2 email: 'In this case, I am only requesting two maps of the city's underground pipelines, which will inform our firm's current work advising the city on wastewater management.' (cung cấp thông tin cho công việc hiện tại của công ty chúng tôi là tư vấn cho thành phố về quản lý nước thải).\n- 'Inform our firm's work advising the city' = 'help his company advise the city'.\n- Phương án đúng: (B) Giúp công ty của ông trong việc tư vấn cho thành phố."
    },
    {
        "id": "test1-q193",
        "group_id": "test1-p7-g191_195",
        "part": 7,
        "question_number": 193,
        "question_type_tag": "detail_lookup",
        "question_text": "What does the sign indicate visitors must do before entering a building?",
        "options": {
            "A": "Go through a security screening",
            "B": "Get a parking permit",
            "C": "Present some identification",
            "D": "Sign a logbook"
        },
        "correct_answer": "D",
        "evidence_quote": "Visitors must sign in prior to entering this facility.",
        "paraphrase_pair": {
            "original": "enter your name and the room you will visit in the logbook",
            "paraphrased": "Sign a logbook"
        },
        "explanation_vi": "Phân tích câu hỏi: Tấm biển thông báo chỉ ra khách tham quan bắt buộc phải làm gì trước khi vào tòa nhà?\n- Dẫn chứng trong bài: Biển hiệu (Văn bản 3): 'Visitors must sign in prior to entering this facility. Please enter your name and the room you will visit in the logbook' (Khách phải đăng ký trước khi vào. Vui lòng ghi tên bạn và phòng bạn sẽ đến vào sổ theo dõi).\n- Phương án đúng: (D) Ký vào sổ ghi chép (Sign a logbook)."
    },
    {
        "id": "test1-q194",
        "group_id": "test1-p7-g191_195",
        "part": 7,
        "question_number": 194,
        "question_type_tag": "cross_text_inference",
        "question_text": "What was Mr. Brandenberg expecting to receive?",
        "options": {
            "A": "An itemized statement of fees",
            "B": "A letter from his company",
            "C": "A phone call from a city official",
            "D": "A password for the Web portal"
        },
        "correct_answer": "A",
        "evidence_quote": "you will receive an itemized statement detailing the services provided and the charges for those specific services.",
        "paraphrase_pair": {
            "original": "itemized statement detailing the services... there was no explanation",
            "paraphrased": "An itemized statement of fees"
        },
        "explanation_vi": "Phân tích câu hỏi liên kết văn bản:\n- Bản hướng dẫn (Văn bản 1, mục 4) quy định: 'If there are any fees associated with your request, you will receive an itemized statement detailing the services provided and the charges for those specific services.' (Nếu có bất kỳ khoản phí nào, bạn sẽ nhận được một bảng kê chi tiết các dịch vụ được cung cấp và mức phí tương ứng).\n- Trong email (Văn bản 2), ông Brandenberg phàn nàn: 'Apparently, I am being charged $300 for my documents. I do not understand why the fee is so high, and there was no explanation included in your e-mail.'\n- Rõ ràng ông Brandenberg đã mong đợi nhận được một bảng kê chi tiết các khoản phí ('itemized statement of fees') như quy trình đã nêu.\n- Phương án đúng: (A) Bảng kê chi tiết các khoản phí (An itemized statement of fees)."
    },
    {
        "id": "test1-q195",
        "group_id": "test1-p7-g191_195",
        "part": 7,
        "question_number": 195,
        "question_type_tag": "cross_text_inference",
        "question_text": "What room will Mr. Brandenberg most likely visit?",
        "options": {
            "A": "Room 100",
            "B": "Room 101",
            "C": "Room 102",
            "D": "Room 103"
        },
        "correct_answer": "D",
        "evidence_quote": "Wastewater — Room 103",
        "paraphrase_pair": {
            "original": "advising the city on wastewater management -> Wastewater Department",
            "paraphrased": "Room 103"
        },
        "explanation_vi": "Phân tích câu hỏi liên kết 3 văn bản:\n- Trong email (Văn bản 2), ông Brandenberg cho biết ông đến lấy tài liệu liên quan đến công việc tư vấn cho thành phố về quản lý nước thải ('wastewater management').\n- Trong bản chỉ dẫn các phòng ở tầng 1 (Văn bản 3): 'Wastewater — Room 103'.\n- Suy luận logic: Ông Brandenberg sẽ đến phòng Quản lý Nước thải (Phòng 103) để nhận tài liệu này.\n- Phương án đúng: (D) Phòng 103 (Room 103)."
    },

    # -------------------------------------------------------------------------
    # Group 15: 196-200 (test1-p7-g196_200)
    # -------------------------------------------------------------------------
    {
        "id": "test1-q196",
        "group_id": "test1-p7-g196_200",
        "part": 7,
        "question_number": 196,
        "question_type_tag": "detail_lookup",
        "question_text": "What does the review mention about Mr. Eklund?",
        "options": {
            "A": "He enjoys his work as a director.",
            "B": "He has been a mentor to many young people.",
            "C": "He is a well-known actor.",
            "D": "He has written many books."
        },
        "correct_answer": "C",
        "evidence_quote": "Mr. Eklund has long been a captivating actor on stage and screen",
        "paraphrase_pair": {
            "original": "storied career as an actor... long been a captivating actor on stage and screen",
            "paraphrased": "He is a well-known actor"
        },
        "explanation_vi": "Phân tích câu hỏi: Bài đánh giá đề cập điều gì về ông Eklund?\n- Dẫn chứng trong bài: Bài báo mở đầu bằng: 'Fans of Simon Eklund will be delighted with his autobiography, The Theatre Lights Dimmed, the first book he has written in his storied career as an actor.' và kết luận: 'Mr. Eklund has long been a captivating actor on stage and screen...'\n- 'Storied career as an actor' (sự nghiệp diễn xuất lẫy lừng) và 'captivating actor' cho thấy ông là một diễn viên rất nổi tiếng và tài năng.\n- Phương án đúng: (C) Ông ấy là một diễn viên nổi tiếng (well-known actor).\n- Bẫy đề thi: (D) viết nhiều sách (sai, bài ghi đây là 'the first book he has written')."
    },
    {
        "id": "test1-q197",
        "group_id": "test1-p7-g196_200",
        "part": 7,
        "question_number": 197,
        "question_type_tag": "cross_text_inference",
        "question_text": "Where most likely will Ms. Joshi meet Mr. Eklund?",
        "options": {
            "A": "In Sweden",
            "B": "In France",
            "C": "In Italy",
            "D": "In the United Kingdom"
        },
        "correct_answer": "A",
        "evidence_quote": "his native Sweden",
        "paraphrase_pair": {
            "original": "native Sweden -> his home country",
            "paraphrased": "In Sweden"
        },
        "explanation_vi": "Phân tích câu hỏi liên kết 2 văn bản:\n- Văn bản 1 (Review) cho biết quê hương gốc của ông Eklund là Thụy Điển: 'starting with his first roles in cinema in his native Sweden... in Stockholm'.\n- Văn bản 2 (Email của Uma Joshi): 'In a helpful coincidence, I will be visiting his home country next month to address a journalists' convention... I'm sure we can set up something with Mr. Eklund just before or after my speech.'\n- Quê hương ('home country') của ông Eklund chính là Thụy Điển (Sweden).\n- Phương án đúng: (A) Tại Thụy Điển (In Sweden)."
    },
    {
        "id": "test1-q198",
        "group_id": "test1-p7-g196_200",
        "part": 7,
        "question_number": 198,
        "question_type_tag": "detail_lookup",
        "question_text": "According to the first e-mail, what is one reason Ms. Joshi will travel in April?",
        "options": {
            "A": "To go on a vacation",
            "B": "To interview for a new job",
            "C": "To attend an international film festival",
            "D": "To speak at a conference"
        },
        "correct_answer": "D",
        "evidence_quote": "I will be visiting his home country next month to address a journalists' convention. I am the featured speaker and will discuss the benefits of diversity in journalism.",
        "paraphrase_pair": {
            "original": "address a journalists' convention. I am the featured speaker",
            "paraphrased": "speak at a conference"
        },
        "explanation_vi": "Phân tích câu hỏi: Theo bức email đầu tiên, một trong những lý do cô Joshi đi công tác vào tháng Tư là gì?\n- Dẫn chứng trong bài: '...I will be visiting his home country next month to address a journalists' convention. I am the featured speaker and will discuss the benefits of diversity in journalism.' (Tôi sẽ đến thăm quê hương của ông ấy vào tháng tới để phát biểu tại hội nghị các nhà báo. Tôi là diễn giả chính...).\n- 'Address a convention' = 'speak at a conference' (phát biểu tại một hội nghị).\n- Phương án đúng: (D) Để phát biểu tại một hội nghị (To speak at a conference)."
    },
    {
        "id": "test1-q199",
        "group_id": "test1-p7-g196_200",
        "part": 7,
        "question_number": 199,
        "question_type_tag": "intent",
        "question_text": "What is the purpose of the second e-mail?",
        "options": {
            "A": "To reserve a hotel room",
            "B": "To confirm meeting arrangements",
            "C": "To discuss an idea for a movie",
            "D": "To ask for transportation"
        },
        "correct_answer": "B",
        "evidence_quote": "We have arranged transportation for you from your hotel to Mr. Eklund's house and then back to the hotel.",
        "paraphrase_pair": {
            "original": "finalize a few details... arranged transportation... stay for lunch",
            "paraphrased": "confirm meeting arrangements"
        },
        "explanation_vi": "Phân tích câu hỏi: Mục đích chính của bức email thứ hai (của cô Maria Cazalla) là gì?\n- Dẫn chứng trong bài: 'I just wanted to finalize a few details with you. We have arranged transportation for you from your hotel to Mr. Eklund's house and then back to the hotel. Please let me know how many people there will be in your group, because Mr. Eklund would like you all to stay for lunch.' (Tôi chỉ muốn chốt lại một số chi tiết với cô. Chúng tôi đã thu xếp xe đưa đón... và mời mọi người dùng bữa trưa).\n- Việc chốt chi tiết đưa đón và lịch hẹn chính là xác nhận các sắp xếp cho buổi gặp mặt = 'To confirm meeting arrangements'.\n- Phương án đúng: (B) Xác nhận các sắp xếp cho cuộc gặp."
    },
    {
        "id": "test1-q200",
        "group_id": "test1-p7-g196_200",
        "part": 7,
        "question_number": 200,
        "question_type_tag": "cross_text_inference",
        "question_text": "What can be concluded about Mr. Eklund?",
        "options": {
            "A": "He hopes to write for a British news site.",
            "B": "He just hired a new assistant.",
            "C": "He was pleased with Ms. Joshi's review of his book.",
            "D": "He frequently cooks special meals."
        },
        "correct_answer": "C",
        "evidence_quote": "He enjoys all your writing for Top News U.K.—the news stories, interviews, and, of course, your recent article about <em>The Theatre Lights Dimmed</em>!",
        "paraphrase_pair": {
            "original": "enjoys all your writing... recent article about The Theatre Lights Dimmed",
            "paraphrased": "pleased with Ms. Joshi's review of his book"
        },
        "explanation_vi": "Phân tích câu hỏi liên kết 3 văn bản:\n- Văn bản 1 là bài review của Uma Joshi về cuốn hồi ký 'The Theatre Lights Dimmed' của ông Eklund.\n- Văn bản 3 (Email của Maria Cazalla gửi cô Joshi): 'He enjoys all your writing for Top News U.K.—the news stories, interviews, and, of course, your recent article about The Theatre Lights Dimmed!' (Ông ấy rất thích các bài viết của cô cho Top News U.K... và dĩ nhiên là bài viết gần đây của cô về cuốn The Theatre Lights Dimmed!).\n- Điều này chứng minh ông Eklund rất hài lòng và thích thú với bài đánh giá sách của cô Joshi.\n- Phương án đúng: (C) Ông ấy hài lòng với bài đánh giá cuốn sách của ông do cô Joshi viết."
    }
]

print(f"Defined {len(part7_questions)} questions.")
