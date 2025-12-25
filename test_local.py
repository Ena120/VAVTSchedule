import pdfplumber
import pandas as pd
import os

def local_convert(pdf_path, xlsx_path):
    print(f"⚙️ Обрабатываю: {pdf_path}")
    
    all_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"   Страниц в файле: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            # Извлекаем таблицу
            # pdfplumber пытается сам определить границы
            table = page.extract_table()
            
            if table:
                print(f"   ✅ На странице {i+1} найдена таблица ({len(table)} строк)")
                # Добавляем данные
                for row in table:
                    # Заменяем None на пустые строки для красоты
                    clean_row = [cell if cell is not None else "" for cell in row]
                    all_data.append(clean_row)
            else:
                print(f"   ⚠️ На странице {i+1} таблица не найдена (возможно, там просто текст).")

    if all_data:
        # Сохраняем в Excel
        df = pd.DataFrame(all_data)
        df.to_excel(xlsx_path, index=False, header=False)
        print(f"🎉 Готово! Файл сохранен как: {xlsx_path}")
    else:
        print("❌ Не удалось вытащить данные. Возможно, PDF картинкой или нестандартный.")

if __name__ == "__main__":
    # Ищем первый попавшийся PDF в папке downloads
    target_pdf = None
    for root, dirs, files in os.walk("downloads"):
        for file in files:
            if file.endswith(".pdf"):
                target_pdf = os.path.join(root, file)
                break
        if target_pdf: break
    
    if target_pdf:
        # Сохраняем результат в корень, чтобы ты сразу увидел
        output_xlsx = "TEST_LOCAL_RESULT.xlsx"
        local_convert(target_pdf, output_xlsx)
    else:
        print("❌ В папке downloads нет PDF файлов! Сначала запусти downloader.py")