from typing import Optional
from loguru import logger
import httpx


class LLMRequest:
    def __init__(self, base_url: str, api_key: str, model: str,timeout: Optional[float],max_tokens= 3000):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens



    async def send_image(self, system_prompt: str, image_b64: str):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content':  [{
                            "type": "image_url",
                            "image_url": {
                                "url": image_b64,
                                "detail":"high"
                            }
                        }]
                    }
                ],
                "stream": False,
                "response_format": {"type": 'text'},
                "temperature": 0.7,
                "max_tokens": self.max_tokens
            }
            logger.debug(f'send llm request, payload: {payload}')
            res = await client.post(url=f'{self.base_url}/chat/completions', headers={
                'Authorization': f'Bearer {self.api_key}'
            }, json=payload)
            logger.debug(f'llm result: {res.text}')

            res.raise_for_status()

            json1 = res.json()
            content_text = json1['choices'][0]['message']['content'].strip()

            # 如果有reasoning_content，也logger打印出来
            if 'reasoning_content' in json1['choices'][0]['message']:
                reasoning_content = json1["choices"][0]["message"]["reasoning_content"]
                logger.debug(f'llm reasoning_content: {reasoning_content}')
            usage = json1['usage']
            logger.debug(f'llm token usage: {usage["total_tokens"]}')
            return content_text