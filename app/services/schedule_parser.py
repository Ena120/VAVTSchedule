import json
import openpyxl
import re

def get_merged_value(sheet, row, col):
    """
    Проверяет, входит ли ячейка в объединенный диапазон,
    и возвращает значение из главной (левой верхней) ячейки.
    """
    cell = sheet.cell(row, col)
    for merged_range in sheet.merged_cells.ranges:
        if cell.coordinate in merged_range:
            return sheet.cell(merged_range.min_row, merged_range.min_col).value
    return cell.value

def parse_schedule(file_path):
    """
    Парсит XLSX файл расписания и возвращает список словарей (JSON).
    """
    wb = openpyxl.load_workbook(file_path, data_only=True) # data_only=True важно, чтобы читать значения, а не формулы
    sheet = wb.active
    
    schedule_data = []
    
    # --- 1. Находим строку с заголовками (группами) ---
    header_row_index = -1
    group_columns = {} # {индекс_колонки: "название_группы"}
    
    # Регулярное выражение для групп ВАВТ (Например: Б24М-..., Б22..., М23...)
    # Ищет строку, начинающуюся на букву, потом цифры, потом дефис
    group_pattern = re.compile(r'^[А-ЯA-Z]\d{2}.*') 

    for row_num in range(1, 20): # Ищем в первых 20 строках
        row_values = []
        for c in range(1, 30):
            val = sheet.cell(row=row_num, column=c).value
            if val:
                row_values.append(str(val).strip())
        
        # Считаем, сколько ячеек в этой строке похожи на группы
        # Если нашли хотя бы 2 ячейки, похожие на группы - это шапка
        matches = sum(1 for v in row_values if group_pattern.match(v))
        
        if matches >= 1: # Достаточно даже 1 группы, чтобы понять, что это шапка
            header_row_index = row_num
            print(f"🔎 Нашел строку с группами: №{row_num}")
            break
            
    if header_row_index == -1:
        # Если не нашли по маске, попробуем поискать просто слово "группа" в строке выше
        # Но для начала выбросим ошибку, чтобы ты видел
        raise ValueError("Не могу найти строку с названиями групп (искал коды вида Б24..., Б22...).")
        
    # Заполняем словарь групп из найденной строки
    for col_num in range(1, sheet.max_column + 1):
        cell_value = sheet.cell(row=header_row_index, column=col_num).value
        # Берем ячейку, если она похожа на группу
        if cell_value and isinstance(cell_value, str) and group_pattern.match(cell_value.strip()):
            group_columns[col_num] = cell_value.strip()

    print(f"🎓 Найдены группы: {list(group_columns.values())}")

    # --- 2. Проходим по строкам и собираем данные ---
    current_day = None
    
    # Начинаем со следующей строки после шапки
    for row_num in range(header_row_index + 1, sheet.max_row + 1):
        
        # --- А. Ищем ДЕНЬ НЕДЕЛИ (обычно 1 колонка) ---
        day_val = get_merged_value(sheet, row_num, 1) 
        if day_val and isinstance(day_val, str) and len(day_val) > 2:
            # Очистка мусора (иногда там "Пн 22.12")
            current_day = day_val.replace('\n', ' ').strip()

        # --- Б. Ищем ВРЕМЯ (обычно 2 колонка) ---
        time_val = get_merged_value(sheet, row_num, 2)
        
        # Если времени нет, это может быть пустая строка или разделитель -> пропускаем
        if not time_val:
            continue
            
        # Нормализация времени (убираем лишнее)
        time_str = str(time_val).replace('\n', '').strip()
        # Проверка: если в "времени" слишком много букв, это не время (бывает заголовок дня)
        if len(time_str) > 20: 
            continue

        # --- В. Проходим по колонкам ГРУПП ---
        for col_idx, group_name in group_columns.items():
            subject_raw = get_merged_value(sheet, row_num, col_idx)
            
            # Если в ячейке что-то есть
            if subject_raw and isinstance(subject_raw, str):
                cleaned_text = subject_raw.replace('\n', ' ').strip()
                
                if len(cleaned_text) < 3: # Игнорируем мусор типа "." или "-"
                    continue
                    
                schedule_data.append({
                    "day": current_day,
                    "time": time_str,
                    "group": group_name,
                    "subject_raw": cleaned_text
                })
                
    return schedule_data