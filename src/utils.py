import base64
import os


def get_base64_str(filename: str) :
    with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    # 根据文件扩展名确定 MIME 类型
    _, ext = os.path.splitext(filename)
    mime_type = f"image/{ext[1:]}" if ext else "image/*"

    if mime_type == 'image/jpg':
        mime_type = 'image/jpeg'

    return f"data:{mime_type};base64,{encoded_string}"