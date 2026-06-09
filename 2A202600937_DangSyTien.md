# Báo Cáo Thu Hoạch Bài Lab: Xây Dựng Hệ Thống Multi-Agent với A2A Protocol

**Họ và tên:** Đặng Sỹ Tiến
**MSHV:** 2A202600937
**Khóa / Lớp:** Batch02 - Day9  

---

## I. TỔNG QUAN
Báo cáo này trình bày chi tiết các bước thực hiện, kết quả cấu hình và mã nguồn được tùy chỉnh dựa trên yêu cầu của Codelab. Hệ thống đã được nâng cấp thành công từ một mô hình gọi LLM trực tiếp, đến hệ thống RAG với công cụ, sau đó là ReAct Agent và cuối cùng là một hệ thống Multi-Agent phân tán theo giao thức A2A.

---

## II. THỰC HIỆN CÁC BÀI TẬP THỰC HÀNH (STAGES 1 - 5)

### Phần 1: Direct LLM Calling
- **Bài Tập 1.1:** Đã thay đổi biến `QUESTION` thành các câu hỏi pháp lý bằng tiếng Việt để kiểm tra khả năng xử lý ngôn ngữ tự nhiên của LLM.
- **Bài Tập 1.2:** Đã thêm cấu hình `temperature=0.3` vào hàm `get_llm()` trong tệp `common/llm.py` nhằm giảm tính ngẫu nhiên (ảo giác), giúp câu trả lời của mô hình mang tính chuyên ngành và nhất quán hơn.

### Phần 2: LLM + RAG & Tools
- **Bài Tập 2.1 (Thay thế Data):** Thay vì dùng dữ liệu Luật Lao động, tôi đã trích xuất từ file PDF và thêm mới các dữ liệu (Knowledge Base Entry) về **Luật Phòng, chống ma túy và Bộ luật Hình sự về tội phạm ma túy** vào biến `LEGAL_KNOWLEDGE` trong `stages/stage_2_rag_tools/main.py` và `exercises/exercise_2_tools.py`.
- **Bài Tập 2.2 (Thêm Tool tính án phạt):** Thiết kế thành công công cụ (Tool) `@tool def check_drug_penalty(crime_type: str, weight_grams: float) -> str:`. Tool này tự động đối chiếu các quy định tại Điều 248, 249, 250, 251 để trả về khung hình phạt dựa trên loại tội danh và khối lượng ma túy bị bắt giữ.

### Phần 3: Single Agent với ReAct
- **Bài Tập 3.1:** Thêm Tool `search_case_law` vào hệ thống. Agent giờ đây có khả năng tra cứu các án lệ nổi tiếng tương ứng với các từ khóa hợp đồng (vd: *Hadley v. Baxendale*, *Carlill v. Carbolic Smoke Ball Co*).
- **Bài Tập 3.2:** Bật chế độ `verbose=True` để theo dõi và gỡ lỗi (debug) quá trình Reasoning. Qua log, có thể thấy rõ chu trình của Agent: **Think** (Suy nghĩ xem cần dùng tool nào) -> **Action** (Gọi Tool) -> **Observe** (Nhận kết quả) -> Trả lời cuối cùng.

### Phần 4: Multi-Agent In-Process
- **Bài Tập 4.1 & 4.2 (Tích hợp Privacy Agent & Conditional Routing):** 
  - Khai báo thêm `privacy_agent` chuyên trách về mảng Bảo vệ dữ liệu cá nhân & GDPR trong cả hai file `exercises/exercise_4_multiagent.py` và file chính `stages/stage_4_milti_agent/main.py`.
  - Cập nhật hàm `check_routing` để tự động điều hướng luồng dữ liệu sang `privacy_agent` khi câu hỏi có chứa các từ khóa: *"data", "privacy", "gdpr", "dữ liệu"*.
  - Sửa hàm `aggregate_results` (hoặc `aggregate`) để thu thập và gộp chung phân tích của mảng bảo mật vào bản báo cáo cuối.
- **Bài Tập (Vẽ Graph sơ đồ):** Đã bổ sung mã nguồn hỗ trợ in hoặc lưu file ảnh (Mermaid Diagram) cấu trúc luồng chạy của Multi-Agent thông qua hàm `graph.get_graph().draw_mermaid_png()` vào cuối file `stages/stage_4_milti_agent/main.py`. Hình ảnh được tự động xuất ra file `multi_agent_graph.png`.

### Phần 5: Distributed A2A System
- **Bài Tập 5.1 (Trace request flow):** Đã theo dõi luồng request thông qua `trace_id`. Dưới đây là sơ đồ luồng dữ liệu (Sequence Diagram) mô tả quá trình giao tiếp giữa các vi dịch vụ (Agents) qua Registry:
  ```mermaid
  sequenceDiagram
      actor User as Người Dùng
      participant Customer as Customer Agent (10100)
      participant Registry as Registry Service (10000)
      participant Law as Law Agent (10101)
      participant Tax as Tax Agent (10102)
      participant Compliance as Compliance Agent (10103)

      User->>Customer: Gửi câu hỏi pháp lý
      Customer->>Registry: Lookup Law Agent
      Registry-->>Customer: Trả về địa chỉ Law Agent
      Customer->>Law: HTTP POST (Câu hỏi + trace_id)
      
      Note over Law: Phân tích pháp lý chung & <br>Quyết định gọi chuyên gia
      
      Law->>Registry: Lookup Tax Agent & Compliance Agent
      Registry-->>Law: Trả về địa chỉ các Agents
      
      par Gọi Song Song
          Law->>Tax: HTTP POST (Context + trace_id)
          Tax-->>Law: Kết quả phân tích Thuế
      and
          Law->>Compliance: HTTP POST (Context + trace_id)
          Compliance-->>Law: Kết quả Tuân thủ
      end
      
      Note over Law: Tổng hợp (Aggregate) kết quả
      Law-->>Customer: Báo cáo đầy đủ
      Customer-->>User: Hiển thị phản hồi
  ```
- **Bài Tập 5.2 (Test dynamic discovery):** Khởi chạy thành công kiến trúc vi dịch vụ (Microservices). Tiến hành tắt đột ngột Tax Agent và quan sát log để xác nhận hệ thống báo lỗi linh hoạt, phản ánh đúng tính chất Dynamic Discovery của Registry.
- **Bài Tập 5.3 (Modify Agent Behavior):** Đã sửa đổi System Prompt trong `tax_agent/graph.py` để yêu cầu Agent trả lời ngắn gọn hơn (*"Keep your response under 50 words and be extremely concise"*). Thay đổi này lập tức khiến Tax Agent phản hồi xúc tích, giảm đáng kể số lượng token tiêu thụ.

---

## III. TRẢ LỜI CÂU HỎI ÔN TẬP (PHẦN 6)

**1. Khi nào nên dùng single agent thay vì multi-agent?**
- **Single Agent:** Dành cho các tác vụ đơn giản, luồng suy luận tuyến tính, không yêu cầu độ sâu chuyên môn ở nhiều lĩnh vực khác nhau, hoặc khi cần tiết kiệm chi phí token và tốc độ phản hồi nhanh.
- **Multi-Agent:** Phù hợp khi bài toán phức tạp, đòi hỏi sự kết hợp chuyên môn sâu từ nhiều mảng (như vừa tư vấn luật, vừa tư vấn quy định thuế) hoặc khi hệ thống cần xử lý nhiều tác vụ song song để mang lại cái nhìn đa chiều.

**2. Ưu điểm của A2A protocol so với gRPC hoặc REST thông thường?**
- A2A Protocol tối ưu hóa chuyên biệt cho giao tiếp phi tập trung giữa các Agents. Thay vì chỉ gửi/nhận payload tĩnh như REST, A2A cho phép truyền tải trạng thái suy luận (reasoning state), công cụ và lịch sử ngữ cảnh. Nó cũng cung cấp khả năng Dynamic Discovery qua Registry, giúp các Agents mở rộng tự động.

**3. Làm thế nào để prevent infinite delegation loops trong A2A?**
- Có thể thiết lập cấu hình giới hạn số bước lặp tối đa (`recursion_limit`).
- Truyền kèm một lịch sử (Call History / Visited Agents) bên trong State của LangGraph để một Agent nhận biết nó không được phép ủy quyền lại cho Agent đã từng xử lý yêu cầu đó.

**4. Tại sao cần Registry service? Có thể hardcode URLs không?**
- **Registry Service** đảm nhiệm vai trò Service Discovery. Khi Agents khởi động, chúng báo cáo IP/Port cho Registry. Nếu một Agent chết và khởi động lại ở Port mới, hệ thống vẫn kết nối được bình thường.
- Việc **Hardcode URLs** chỉ chạy được ở môi trường Lab nhỏ. Khi hệ thống Scale lên production với nhiều instance, hoặc IP bị thay đổi, Hardcode URL sẽ làm đứt gãy hoàn toàn giao tiếp giữa các Agents.

---

## IV. BÀI TẬP NÂNG CAO (CHALLENGES - TỰ HỌC)

**Challenge 1: Thêm memory/conversation history**
- **Giải pháp đề xuất:** Sử dụng `MemorySaver` của LangGraph (như `SqliteSaver` hoặc `RedisSaver`) truyền vào `checkpointer` khi compile graph. Điều này sẽ tự động lưu lại toàn bộ lịch sử hội thoại dưới một `thread_id` duy nhất, giúp Agent ghi nhớ ngữ cảnh từ các luồng chat trước đó.

**Challenge 2: Add authentication**
- **Giải pháp đề xuất:** Cấu hình FastAPI dependency để yêu cầu `X-API-Key` ở phần header của mỗi request. Phía client (hoặc các Agent gọi lẫn nhau thông qua `A2ASettings`) cũng phải thiết lập để inject API Key này vào HTTP header mỗi khi gửi request A2A.

**Challenge 3: Implement retry logic**
- **Giải pháp đề xuất:** Áp dụng thư viện `tenacity` với decorator `@retry(wait=wait_exponential(multiplier=1, min=2, max=10))` bọc quanh các hàm gửi request HTTP (POST) trong `common/a2a_utils.py` hoặc LangGraph nodes. Điều này đảm bảo khi một sub-agent bị timeout hoặc nghẽn mạng, luồng xử lý sẽ tự động thử lại sau vài giây với cơ chế backoff.

**Challenge 4: Monitoring & Observability**
- **Giải pháp đề xuất:** Khai báo biến môi trường `LANGCHAIN_TRACING_V2=true` và thiết lập `LANGCHAIN_API_KEY` để tự động tích hợp **LangSmith**. Từ đây, toàn bộ quá trình Agent gọi Tools, tiêu thụ bao nhiêu Token, luồng chạy qua các State nào và mất bao nhiêu milliseconds đều được monitor trực quan thông qua giao diện Web của LangChain.

---

## V. BÀI TẬP CỘNG ĐIỂM (BONUS)

**1. Latency (Tổng thời gian trả lời 1 câu hỏi của hệ thống) là bao nhiêu giây?**
- Ở chế độ mặc định (đầy đủ các bước RAG và Agents giao tiếp mạng), hệ thống Multi-Agent tốn khoảng **12 - 18 giây** để trả lời hoàn chỉnh một truy vấn phức tạp.

**2. Đề xuất phương án giảm latency và kết quả Demo:**
Để tối ưu hóa thời gian phản hồi, tôi đã đề xuất và thực thi các phương pháp sau:
- **Tối ưu Mô hình (Model):** Sử dụng `gpt-4o-mini` - phiên bản nhẹ, chi phí rẻ và trả lời cực nhanh, giúp cải thiện tốc độ đáng kể so với model lớn.
- **Xử lý Song Song (Parallel Execution):** Tận dụng tính năng Send API của LangGraph, điều hướng câu hỏi đến Tax Agent, Compliance Agent và Privacy Agent **cùng một lúc** thay vì chờ tuần tự.
- **Giới hạn số token đầu ra (Concise Prompting):** Thêm vào System Prompt của Agent yêu cầu "Trả lời siêu ngắn gọn dưới 50 từ" (Như đã làm tại bài tập 5.3). 

=> **Kết quả:** Sau khi áp dụng các phương án tối ưu, thời gian xử lý đã giảm mạnh xuống chỉ còn khoảng **6 - 9 giây**, tốc độ hệ thống tăng lên ~50%.

---
**-- HẾT --**
