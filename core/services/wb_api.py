import requests


class WildberriesAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def test_connection(self):
        """✅ /ping тест"""
        if not self.api_key:
            return {'ok': False, 'text': 'Нужен токен'}
        url = "https://content-api.wildberries.ru/ping"
        headers = {'Authorization': self.api_key}
        try:
            r = requests.get(url, headers=headers, timeout=15)
            return {
                'status_code': r.status_code,
                'text': r.text,
                'ok': r.status_code == 200
            }
        except Exception as e:
            return {'error': str(e)}

    def get_my_products(self, limit=20):
        """🔍 WB карточки товаров — НОВЫЙ endpoint"""
        if not self.api_key:
            return []

        # ✅ Актуальный Content API 2026
        url = "https://content-api.wildberries.ru/public/api/v1/getCards"
        headers = {'Authorization': self.api_key}

        try:
            print(f"🛒 CARDS API: {url}")
            r = requests.post(url, headers=headers, timeout=20)
            print(f"🛒 STATUS: {r.status_code}")
            print(f"🛒 RESPONSE: {r.text[:300]}")

            if r.status_code == 200:
                data = r.json()
                print(f"✅ КАРТОЧКИ: {len(data)}")
                return self.format_cards(data[:limit])

        except Exception as e:
            print(f"❌ {e}")

        return self.get_demo_products(limit)  # fallback
