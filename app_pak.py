import subprocess
import sys
import os
from dotenv import load_dotenv
from loguru import logger
import shutil


load_dotenv()

logger.remove()
logger.add(sys.stdout, level=os.getenv('LOGGER_LEVEL'))

OCR_PATH = os.path.join(os.getenv('DANGO_TRANSLATOR_DIR'), 'ocr')
BAK_PATH = os.path.join(os.getenv('DANGO_TRANSLATOR_DIR'), 'ocr_bak')

if not os.path.exists(BAK_PATH) and os.path.exists(OCR_PATH):
    os.renames(OCR_PATH, BAK_PATH)


current_dir = os.path.dirname(os.path.abspath(__file__))

command = [
    sys.executable, "-m", "PyInstaller", 'src/ocr_server.py',
    '--clean','--onefile',
    "--distpath", OCR_PATH,
    '--name', 'startOCR',
    "--paths", os.path.join(current_dir, "src")
]

try:
    # capture_output=True 可以捕获stdout和stderr
    # text=True 解码stdout/stderr为文本
    # check=True 会在命令返回非零退出码时抛出CalledProcessError
    result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    logger.info('打包完成！')
except Exception as e:
    logger.exception(f"PyInstaller 打包出错: {e}")

#打包完毕，把.env文件复制过去
shutil.copy('.env', os.path.join(OCR_PATH, '.env'))