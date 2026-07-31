import requests
from config import CONFIG
import time

def get_wildberries_products():
    all_accounts_items = {}
    
    for account in CONFIG['WILDBERRIES_ACCOUNTS']:
        print(f"Получаем данные с Wildberries ({account['name']})...")
        try:
            account_items = get_wb_account_products(account['Api-key'], account['name'])
            all_accounts_items[account['name']] = account_items
            time.sleep(1)
        except Exception as e:
            print(f"Ошибка при получении товаров с Wildberries ({account['name']}): {e}")
            # Создаем пустой словарь для этого аккаунта в случае ошибки
            all_accounts_items[account['name']] = {}
            continue
    
    return all_accounts_items

def get_wb_account_products(api_key, account_name):
    url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    items_with_stock = {}
    cursor = None
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        payload = {
            "settings": {
                "cursor": {
                    "limit": 100,
                    **({"updatedAt": cursor["updatedAt"], "nmID": cursor["nmID"]} if cursor else {})
                },
                "filter": {
                    "withPhoto": -1
                }
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 429:
                wait_time = int(response.headers.get('Retry-After', 5))
                print(f"{account_name}: Достигнут лимит запросов. Ждем {wait_time} секунд...")
                time.sleep(wait_time)
                retry_count += 1
                continue
                
            response.raise_for_status()
            data = response.json()
            
            for card in data.get('cards', []):
                if 'vendorCode' in card and card['vendorCode'] in CONFIG['PRODUCTS']:
                    quantity = card.get('sizes', [{}])[0].get('stocks', [{}])[0].get('qty', 1)
                    items_with_stock[card['vendorCode']] = quantity > 0
            
            if 'cursor' not in data or len(data['cards']) < 100:
                break
                
            cursor = data['cursor']
            retry_count = 0
            time.sleep(1)
            
        except Exception as e:
            print(f"{account_name}: Ошибка Wildberries API: {e}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(5)
            else:
                break
    
    print(f"{account_name}: обработано {len(items_with_stock)} товаров")
    return items_with_stock