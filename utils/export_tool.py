from db.db_operate import query_valid_records

def export_to_md(save_path):
    records = query_valid_records()
    md_content = "# 剪贴板历史记录导出\n\n"
    for row in records:
        rid, c_type, content, _, create_time = row
        md_content += f"## {create_time}\n"
        md_content += f"类型：{c_type}\n"
        if c_type == "text" and content:
            md_content += f"```\n{content}\n```\n\n"

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(md_content)

def export_to_txt(save_path):
    records = query_valid_records()
    txt_content = ""
    for row in records:
        rid, c_type, content, _, create_time = row
        txt_content += f"[{create_time}] [{c_type}] {content}\n\n"
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(txt_content)