"""Bài Tập 2: Thêm Tools và Knowledge Base

Hoàn thành các TODO để thêm tool và knowledge base entry mới.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from common.llm import get_llm

# Knowledge base
LEGAL_KNOWLEDGE = [
    {
        "id": "ucc_breach",
        "keywords": ["breach", "contract", "remedies", "damages", "ucc"],
        "text": (
            "Under the Uniform Commercial Code (UCC) Article 2, remedies for breach of contract "
            "include: (1) expectation damages; (2) consequential damages; (3) specific performance; "
            "(4) cover damages. Statute of limitations is typically 4 years (UCC § 2-725)."
        ),
    },
    {
        "id": "drug_possession",
        "keywords": ["tàng trữ", "ma túy", "trái phép", "điều 249", "bộ luật hình sự"],
        "text": (
            "Theo Điều 249 Bộ luật Hình sự 2015 (sửa đổi, bổ sung 2017), tội tàng trữ trái phép chất ma túy "
            "bị phạt tù từ 03 năm đến 05 năm đối với khối lượng ma túy nhỏ (ví dụ: Heroine từ 0,1g đến dưới 5g). "
            "Phạm tội có tổ chức hoặc khối lượng lớn hơn (ví dụ: Heroine từ 5g đến dưới 30g) bị phạt tù từ 05 năm đến 10 năm. "
            "Nếu khối lượng rất lớn (ví dụ: Heroine từ 100g trở lên) có thể bị phạt tù từ 15 năm đến 20 năm hoặc tù chung thân."
        ),
    },
    {
        "id": "drug_trafficking",
        "keywords": ["vận chuyển", "mua bán", "ma túy", "điều 250", "điều 251"],
        "text": (
            "Theo Điều 250 và Điều 251 Bộ luật Hình sự 2015, tội vận chuyển và tội mua bán trái phép chất ma túy "
            "có mức phạt cơ bản từ 03 năm đến 07 năm tù. Tuy nhiên, nếu phạm tội có tổ chức, qua biên giới, hoặc "
            "khối lượng ma túy lớn, mức phạt có thể tăng lên 07 - 15 năm, 15 - 20 năm, tù chung thân hoặc tử hình. "
            "Đặc biệt, mua bán Heroine từ 100g trở lên có thể đối mặt với án tử hình."
        ),
    },
    {
        "id": "drug_production",
        "keywords": ["sản xuất", "ma túy", "trái phép", "điều 248"],
        "text": (
            "Điều 248 Bộ luật Hình sự quy định Tội sản xuất trái phép chất ma túy với mức phạt cơ bản từ 03 năm đến 07 năm tù. "
            "Phạm tội có tổ chức, tái phạm nguy hiểm hoặc sản xuất số lượng lớn sẽ bị phạt tù từ 07 năm đến 15 năm. "
            "Khối lượng cực lớn (ví dụ: Heroine 3kg trở lên) sẽ bị phạt tù chung thân hoặc tử hình."
        ),
    },
]


@tool
def search_legal_knowledge(query: str) -> str:
    """Tìm kiếm trong knowledge base pháp lý."""
    query_lower = query.lower()
    for entry in LEGAL_KNOWLEDGE:
        if any(kw in query_lower for kw in entry["keywords"]):
            return f"[{entry['id']}] {entry['text']}"
    return "Không tìm thấy thông tin liên quan."


@tool
def check_statute_of_limitations(case_type: str) -> str:
    """Kiểm tra thời hiệu khởi kiện.
    
    Args:
        case_type: Loại vụ án (contract, tort, property)
    """
    limits = {
        "contract": "4 năm (UCC § 2-725)",
        "tort": "2-3 năm tùy bang",
        "property": "5 năm",
    }
    return limits.get(case_type.lower(), "Không xác định")


@tool
def check_drug_penalty(crime_type: str, weight_grams: float) -> str:
    """Kiểm tra mức phạt cơ bản đối với tội phạm về ma túy (đặc biệt là Heroine) dựa trên tội trạng và khối lượng.
    
    Args:
        crime_type: Loại tội phạm (tang_tru, van_chuyen, mua_ban, san_xuat)
        weight_grams: Khối lượng ma túy tính bằng gam
    """
    crime = crime_type.lower()
    
    if "tang_tru" in crime:
        if weight_grams < 0.1: return "Chưa đến mức truy cứu hình sự (Xử lý hành chính)"
        if weight_grams < 5: return "Phạt tù từ 01 năm đến 05 năm (Khoản 1 Điều 249)"
        if weight_grams < 30: return "Phạt tù từ 05 năm đến 10 năm (Khoản 2 Điều 249)"
        if weight_grams < 100: return "Phạt tù từ 10 năm đến 15 năm (Khoản 3 Điều 249)"
        return "Phạt tù từ 15 năm đến 20 năm hoặc chung thân (Khoản 4 Điều 249)"
        
    if "mua_ban" in crime or "van_chuyen" in crime:
        if weight_grams < 0.1: return "Chưa đến mức truy cứu hình sự (Xử lý hành chính)"
        if weight_grams < 5: return "Phạt tù từ 02 năm đến 07 năm (Khoản 1 Điều 250/251)"
        if weight_grams < 30: return "Phạt tù từ 07 năm đến 15 năm (Khoản 2 Điều 250/251)"
        if weight_grams < 100: return "Phạt tù từ 15 năm đến 20 năm (Khoản 3 Điều 250/251)"
        return "Phạt tù 20 năm, tù chung thân hoặc tử hình (Khoản 4 Điều 250/251)"
        
    if "san_xuat" in crime:
        if weight_grams < 5: return "Phạt tù từ 03 năm đến 07 năm (Khoản 1 Điều 248)"
        if weight_grams < 30: return "Phạt tù từ 07 năm đến 15 năm (Khoản 2 Điều 248)"
        if weight_grams < 100: return "Phạt tù từ 15 năm đến 20 năm (Khoản 3 Điều 248)"
        return "Phạt tù 20 năm, tù chung thân hoặc tử hình (Khoản 4 Điều 248)"
        
    return "Không tìm thấy thông tin cho loại tội này. Hỗ trợ: tang_tru, van_chuyen, mua_ban, san_xuat"


async def main():
    load_dotenv()
    llm = get_llm()
    
    # TODO: Thêm tool mới vào danh sách
    tools = [search_legal_knowledge, check_statute_of_limitations, check_drug_penalty]  # Thêm check_drug_penalty vào đây

    llm_with_tools = llm.bind_tools(tools)
    
    question = "Nếu tôi bị bắt vì tàng trữ 40 gam Heroine thì bị phạt bao nhiêu năm tù?"
    
    messages = [
        SystemMessage(content="Bạn là chuyên gia pháp lý. Sử dụng tools để tra cứu thông tin."),
        HumanMessage(content=question),
    ]
    
    print(f"Câu hỏi: {question}\n")
    
    # First LLM call - decide which tools to use
    response = await llm_with_tools.ainvoke(messages)
    messages.append(response)
    
    # Execute tools if requested
    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"🔧 Gọi tool: {tool_call['name']}")
            tool_result = None
            
            if tool_call["name"] == "search_legal_knowledge":
                tool_result = search_legal_knowledge.invoke(tool_call["args"])
            elif tool_call["name"] == "check_statute_of_limitations":
                tool_result = check_statute_of_limitations.invoke(tool_call["args"])
            
            if tool_result:
                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
        
        # Second LLM call - synthesize final answer
        final_response = await llm_with_tools.ainvoke(messages)
        print(f"\n✅ Kết quả:\n{final_response.content}")
    else:
        print(f"\n✅ Kết quả:\n{response.content}")


if __name__ == "__main__":
    asyncio.run(main())
