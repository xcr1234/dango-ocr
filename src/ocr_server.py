import argparse
import os
import sys

from fastapi import FastAPI, Request
from pydantic import BaseModel
from uvicorn import run
from dotenv import load_dotenv
from loguru import logger

from src.ocr import do_ocr


def get_exe_dir():
    """
    获取当前 .exe 文件所在的目录。
    适用于 PyInstaller 打包后的单文件模式。
    """
    if getattr(sys, 'frozen', False):
        # 如果应用程序被 PyInstaller 打包
        # sys.executable 指向 .exe 文件的路径
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境，直接运行 .py 脚本
        return os.path.dirname(os.path.abspath(__file__))

exe_dir = get_exe_dir()
dotenv_path = os.path.join(exe_dir, '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("No .env file found")
    sys.exit(1)

logger.remove()
logger.add(sys.stdout, level=os.getenv('LOGGER_LEVEL'))


app = FastAPI()


class OCRRequest(BaseModel):
    ImagePath: str
    Language: str


@app.post("/ocr/api")
async def ocr(request: OCRRequest):
    logger.info(f'request ocr {request}')

    try:
        ocr_result = await do_ocr(request.ImagePath, request.Language)
    except Exception as e:
        logger.error(f'do_ocr failed: {e}')
        return {
            'Code': -1,
            'message': str(e),
        }

    logger.info(f'ocr result: {ocr_result}')

    return {
        'Code': 0,
        'Message': 'ok',
        'Data':[{
            'Coordinate':{
                'LowerRight': [0,0],
                'UpperRight': [0,0],
                'LowerLeft': [0,0],
                'UpperLeft': [0,0],
            },
            'Words': ocr_result,
            'Score': 1
        }]
    }

@app.post("/chat/completions")
async def chat_completions(request: Request):
    request = await request.json()

    logger.debug(f'chat_completions {request}')

    user_content = request['messages'][-1]['content']

    return {
        'choices': [
            {
                'message': {
                    "role": "assistant",
                    'content': user_content
                }
            }
        ]
    }

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 6666
    path = "/ocr/api"
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--host", type=str, default=host, help="监听的主机。默认：\"%s\"" % host)
    parser.add_argument("-p", "--port", type=int, default=port, help="监听的端口。默认：%d" % port)
    parser.add_argument("-P", "--path", type=str, default=path, help="监听的路径。默认：\"%s\"" % path)
    parser.add_argument('--help', action='help', help='打印帮助。')
    args = parser.parse_args()


    run(app, host=args.host, port=int(args.port))