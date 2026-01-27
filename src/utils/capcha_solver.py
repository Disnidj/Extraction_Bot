import httpx
import asyncio
from .load_yaml import TWO_CAPTCHA_API_KEY

async def solve_captcha(captcha_sitekey, page_url):

    captcha_url = 'http://2captcha.com/in.php'
    solve_url = 'http://2captcha.com/res.php'

    # Send CAPTCHA to 2Captcha for solving
    payload = {
        'key': TWO_CAPTCHA_API_KEY,
        'method': 'userrecaptcha',
        'googlekey': captcha_sitekey,
        'pageurl': page_url,
        'json': 1
    }

    async with httpx.AsyncClient() as client:
        # Step 1: Submit CAPTCHA to 2Captcha
        response = await client.post(captcha_url, data=payload)
        captcha_id = response.json().get('request')

    if not captcha_id:
        raise Exception(f"Failed to send CAPTCHA to 2Captcha: {response.json()}")

    print(f"CAPTCHA sent successfully. CAPTCHA ID: {captcha_id}")

    # Step 2: Polling to get the CAPTCHA solution
    while True:
        await asyncio.sleep(10)  # Increase polling interval to 10 seconds
        payload = {
            'key': TWO_CAPTCHA_API_KEY,
            'action': 'get',
            'id': captcha_id,
            'json': 1
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(solve_url, params=payload)
            response_json = response.json()

            # Check if the CAPTCHA is solved
            if response_json.get('status') == 1:
                print(f"CAPTCHA solved: {response_json['request']}")
                return response_json['request']
            elif response_json.get('status') == 0:
                print(f"CAPTCHA not solved yet. Message: {response_json['request']}")
                if response_json.get('request') != 'CAPCHA_NOT_READY':
                    raise Exception(f"Error solving CAPTCHA: {response_json['request']}")
            else:
                print(f"Error from 2Captcha: {response_json}")
                raise Exception(f"Error solving CAPTCHA: {response_json}")