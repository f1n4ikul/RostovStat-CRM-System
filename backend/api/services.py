import requests
from bs4 import BeautifulSoup
import urllib3

# Отключаем ворнинги SSL для чистоты консоли
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_rostovstat_stats():
    url = "https://61.rosstat.gov.ru/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stats_list = []
        
        # 1. Находим карточку "Оперативные показатели"
        # Мы ищем заголовок, а потом его родительскую карточку
        target_title = soup.find('div', class_='card-universal__title', string=lambda t: t and 'Оперативные показатели' in t)
        
        if target_title:
            # Поднимаемся к общему контейнеру карточки
            parent_card = target_title.find_parent('div', class_='card-universal')
            # Находим все строки с индикаторами
            rows = parent_card.select('.indicators__cols')
            
            for row in rows:
                # В каждой строке несколько блоков .indicators__data
                cols = row.select('.indicators__data')
                
                if len(cols) >= 2:
                    raw_name = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    unit = cols[2].get_text(strip=True) if len(cols) > 2 else ""
                    
                    # Немного чистим название (убираем даты в скобках для красоты)
                    clean_name = raw_name.split('(')[0].split(' в ')[0].strip()
                    
                    stats_list.append({
                        "name": clean_name,
                        "value": f"{value} {unit}".strip()
                    })

        # Если что-то пошло не так, возвращаем заглушку
        return stats_list[:4] if stats_list else get_fallback_stats()
        
    except Exception as e:
        print(f"Парсинг не удался: {e}")
        return get_fallback_stats()

def get_fallback_stats():
    return [
        {"name": "Индекс потребительских цен", "value": "102,2 %"},
        {"name": "Среднемесячная зарплата", "value": "72 306 руб."},
        {"name": "Ввод жилых домов", "value": "318,5 тыс. кв. м."},
        {"name": "Численность работников", "value": "1 022 846 чел."}
    ]

# Для проверки прямо из этого файла:
if __name__ == "__main__":
    data = get_rostovstat_stats()
    import json
    print(json.dumps(data, indent=4, ensure_ascii=False))