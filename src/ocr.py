import os

from loguru import logger

from src.llm_request import LLMRequest
from src.utils import get_base64_str

translate_cache = {}



lang_dict = {
    'JAP': '日语',
    'ENG': '英语',
    'KOR': '韩语',
    'RU': '俄语',
    'ZH': '中文',
}

async def do_ocr(file_path: str, language: str):
    base64_content = get_base64_str(file_path)
    logger.debug(f'base64_content: {base64_content}')

    if base64_content in translate_cache:
        logger.debug('cache hits')
        return translate_cache[base64_content]

    llm_ocr = LLMRequest(
        base_url=os.getenv("OCR_LLM_URL"),
        model=os.getenv("OCR_LLM_MODEL"),
        api_key=os.getenv("OCR_LLM_KEY"),
        timeout=None
    )

    llm_result = await llm_ocr.send_image(f'请识别图片中的文字，文字语言是{lang_dict.get(language, language)}；直接输出识别结果，不输出多余内容，并把其中的换行符替换成空格', base64_content)

    translate_cache[base64_content] = llm_result

    return llm_result