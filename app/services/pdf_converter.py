import pdfplumber
import pandas as pd
import os

def convert_pdf_to_xlsx(pdf_path, xlsx_path):
    """
    Конвертирует PDF в Excel локально с помощью pdfplumber.
    Не требует ключей и интернета.
    """
    print(f"⚙️ [Local] Конвертация: {pdf_path}")
    
    try:
        all_data = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Извлекаем таблицу
                table = page.extract_table()
                if table:
                    for row in table:
                        # Заменяем None на пустые строки
                        clean_row = [cell if cell is not None else "" for cell in row]
                        all_data.append(clean_row)
        
        if all_data:
            df = pd.DataFrame(all_data)
            # Сохраняем без заголовков и индекса
            df.to_excel(xlsx_path, index=False, header=False)
            print(f"✅ Успешно сконвертировано: {xlsx_path}")
            return True
        else:
            print(f"⚠️ В файле не найдено таблиц: {pdf_path}")
            return False

    except Exception as e:
        print(f"❌ Ошибка локальной конвертации: {e}")
        return False