import aiohttp
import asyncio
from bs4 import BeautifulSoup
import os
from urllib.parse import unquote

# Базовый URL
BASE_URL = "https://www.vavt.ru"
START_URL = "https://www.vavt.ru/schedule/?f=%D0%91%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80%D0%B8%D0%B0%D1%82&o=%D0%9E%D1%87%D0%BD%D0%B0%D1%8F+%D1%84%D0%BE%D1%80%D0%BC%D0%B0+%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D1%8F"
DOWNLOAD_DIR = "downloads"

# Что мы ищем
TARGET_FACULTIES = ['МПФ', 'ФВМ', 'ФМФ', 'ФЭМ']
TARGET_COURSES = ['1 курс', '2 курс', '3 курс', '4 курс']

async def get_soup(session, url):
    """Скачивает HTML страницы и делает из него суп"""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                return BeautifulSoup(html, "lxml")
    except Exception as e:
        print(f"❌ Ошибка соединения с {url}: {e}")
    return None

async def download_file(session, url, folder, filename):
    """Скачивает файл в указанную папку"""
    filepath = os.path.join(folder, filename)
    
    # Если файл уже есть, пропускаем (чтобы не качать лишнее)
    if os.path.exists(filepath):
        # print(f"⏭️  Файл уже есть: {filename}")
        return

    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(filepath, 'wb') as f:
                    f.write(content)
                print(f"✅ Скачан: {filename}")
    except Exception as e:
        print(f"❌ Ошибка скачивания {filename}: {e}")

async def main():
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        
        # 1. Заходим на главную, ищем ссылки на факультеты
        print("🔍 Шаг 1: Ищем факультеты...")
        soup = await get_soup(session, START_URL)
        if not soup: return

        faculty_links = {}
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True)
            if text in TARGET_FACULTIES:
                href = a['href']
                faculty_links[text] = href if href.startswith('http') else BASE_URL + href

        # 2. Проходим по каждому факультету
        for fac_name, fac_url in faculty_links.items():
            print(f"\n🏛️  Факультет: {fac_name}")
            fac_soup = await get_soup(session, fac_url)
            if not fac_soup: continue

            # Ищем ссылки на курсы (1 курс, 2 курс...)
            course_links = {}
            for a in fac_soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                # Проверяем, содержит ли текст "1 курс", "2 курс" и т.д.
                for course in TARGET_COURSES:
                    if course in text:
                        href = a['href']
                        course_links[course] = href if href.startswith('http') else BASE_URL + href
            
            # 3. Заходим на каждый курс и качаем PDF
            for course_name, course_url in course_links.items():
                print(f"  🎓 {course_name}...")
                
                # Создаем папку: downloads/МПФ/1 курс
                course_dir = os.path.join(DOWNLOAD_DIR, fac_name, course_name)
                os.makedirs(course_dir, exist_ok=True)

                course_soup = await get_soup(session, course_url)
                if not course_soup: continue

                found_pdfs = 0
                for a in course_soup.find_all('a', href=True):
                    href = a['href']
                    
                    if '.pdf' in href.lower() and 'privacy-policy' not in href:
                        full_url = href if href.startswith('http') else BASE_URL + href
                        
                        # Достаем чистое имя файла из ссылки (декодируем %20 в пробелы)
                        filename = unquote(href.split('/')[-1])
                        
                        await download_file(session, full_url, course_dir, filename)
                        found_pdfs += 1
                
                if found_pdfs == 0:
                    print(f"    ⚠️ PDF не найдены (возможно, только сессия или каникулы)")

if __name__ == "__main__":
    # Запуск
    asyncio.run(main())