import requests
from config import CONFIG
import time

def get_ozon_products():
    all_accounts_items = {}
    
    for account in CONFIG['OZON_ACCOUNTS']:
        print(f"Получаем данные с Ozon ({account['name']})...")
        headers = {
            "Client-Id": account['Client-id'],
            "Api-Key": account['Api-key'],
            "Content-Type": "application/json"
        }
        
        try:
            account_items = req_ozon_info(headers, account['name'])
            all_accounts_items[account['name']] = account_items
            time.sleep(1)
        except Exception as e:
            print(f"Ошибка при получении товаров с Ozon ({account['name']}): {e}")
            all_accounts_items[account['name']] = {}
            continue
    
    return all_accounts_items

def req_ozon_info(headers, account_name):
    products_data = {article: None for article in CONFIG['PRODUCTS']}
    data_article = list(products_data.keys())
    result_items = []
    
    chunk_size = 1000
    for i in range(0, len(data_article), chunk_size):
        chunk = data_article[i:i + chunk_size]
        data_for_post = {
            "offer_id": chunk
        }
        product_info = 'https://api-seller.ozon.ru/v3/product/info/list'
        try:
            response = requests.post(product_info, headers=headers, json=data_for_post)
            response.raise_for_status()
            res = response.json()
            
            if 'result' in res and 'items' in res['result']:
                result_items.extend(res['result']['items'])
            elif 'items' in res:
                result_items.extend(res['items'])
            else:
                print(f'{account_name}: Неожиданный ответ от Ozon API')
                continue
                
        except Exception as e:
            print(f'{account_name}: Ошибка при запросе к Ozon API: {e}')
            continue
    
    items_with_stock = {}
    
    for item in result_items:
        offer_id = item.get('offer_id')
        if not offer_id:
            continue
            
        stocks = item.get('stocks', {}).get('stocks', [])
        present = sum(stock.get('present', 0) for stock in stocks)
        items_with_stock[offer_id] = present > 0
    
    print(f"{account_name}: обработано {len(items_with_stock)} товаров")
    return items_with_stock