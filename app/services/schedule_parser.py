import openpyxl
import re

def parse_schedule(file_path):
    """
    Парсит локально созданный Excel файл.
    Учитывает, что pdfplumber не объединяет ячейки, а оставляет их пустыми.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    
    schedule_data = []
    
    # --- 1. Поиск шапки с группами ---
    header_row_index = -1
    group_columns = {} # {индекс_колонки: "Название группы"}
    
    # Ищем код группы (например Б25Ф..., М23...)
    group_pattern = re.compile(r'^[А-ЯA-Z]\d{2}.*') 

    for row_num in range(1, 20):
        for col_num in range(1, sheet.max_column + 1):
            val = sheet.cell(row=row_num, column=col_num).value
            if val and isinstance(val, str):
                # Чистим от переносов строк
                val = val.replace('\n', '')
                if group_pattern.match(val.strip()):
                    header_row_index = row_num
                    # Собираем все группы в этой строке
                    # Пробегаем по всей строке еще раз
                    for c in range(1, sheet.max_column + 1):
                        g_val = sheet.cell(row=row_num, column=c).value
                        if g_val and isinstance(g_val, str) and len(g_val) > 3:
                             group_columns[c] = g_val.strip().replace('\n', '')
                    break
        if header_row_index != -1:
            break
            
    if header_row_index == -1:
        print(f"⚠️ Не нашел строку с группами в файле {file_path}")
        return []

    print(f"🎓 Найдены группы: {list(group_columns.values())}")

    # --- 2. Чтение данных ---
    current_day = None # Здесь будем хранить "Текущий день" (Пн29.12), пока не встретим новый
    
    for row_num in range(header_row_index + 1, sheet.max_row + 1):
        # Колонка A (1) - День недели
        day_cell = sheet.cell(row=row_num, column=1).value
        
        # Если в ячейке дня что-то написано, обновляем "текущий день"
        if day_cell and str(day_cell).strip():
            current_day = str(day_cell).strip().replace('\n', ' ')
        
        # Если дня еще нет (начало файла мусорное) - пропускаем
        if not current_day:
            continue

        # Колонка B (2) - Время
        time_cell = sheet.cell(row=row_num, column=2).value
        if not time_cell:
            continue # Если нет времени, значит строка пустая или мусорная
        
        time_str = str(time_cell).strip().replace('\n', '')
        
        # Фильтр: Время должно содержать цифры (защита от лишних заголовков)
        if not any(char.isdigit() for char in time_str):
            continue

        # --- 3. Проход по колонкам групп ---
        for col_idx, group_name in group_columns.items():
            subject_val = sheet.cell(row=row_num, column=col_idx).value
            
            # Если ячейка с предметом НЕ пустая - сохраняем
            if subject_val and str(subject_val).strip():
                subject_text = str(subject_val).strip().replace('\n', ' ')
                
                schedule_data.append({
                    "day": current_day,
                    "time": time_str,
                    "group": group_name,
                    "subject_raw": subject_text
                })

    return schedule_data