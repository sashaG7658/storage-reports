from ozon_api import get_ozon_products
from wildberries_api import get_wildberries_products
from excel_report import create_excel_report
from config import CONFIG

def main():
    print("=" * 60)
    print("ПРОВЕРКА НАЛИЧИЯ ТОВАРОВ НА МАРКЕТПЛЕЙСАХ")
    print("=" * 60)
    print(f"Ozon аккаунтов: {len(CONFIG['OZON_ACCOUNTS'])}")
    print(f"Wildberries аккаунтов: {len(CONFIG['WILDBERRIES_ACCOUNTS'])}")
    print(f"Товаров для проверки: {len(CONFIG['PRODUCTS'])}")
    print("=" * 60)
    
    ozon_accounts_items = get_ozon_products()
    wb_accounts_items = get_wildberries_products()
    
    file_path = create_excel_report(CONFIG['PRODUCTS'], ozon_accounts_items, wb_accounts_items)
    
    total_products = len(CONFIG['PRODUCTS'])
    
    print("\n" + "=" * 60)
    print(f"Отчет успешно сохранен: {file_path}")
    print("=" * 60)
    print("СТАТИСТИКА ПО АККАУНТАМ:")
    print("=" * 60)
    
    print("OZON:")
    for account in CONFIG['OZON_ACCOUNTS']:
        account_name = account['name']
        available = sum(1 for product in CONFIG['PRODUCTS'] 
                       if ozon_accounts_items.get(account_name, {}).get(product, False))
        print(f"  {account_name}: {available}/{total_products}")
    
    print("-" * 30)
    
    print("WILDBERRIES:")
    for account in CONFIG['WILDBERRIES_ACCOUNTS']:
        account_name = account['name']
        available = sum(1 for product in CONFIG['PRODUCTS'] 
                       if wb_accounts_items.get(account_name, {}).get(product, False))
        print(f"  {account_name}: {available}/{total_products}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()