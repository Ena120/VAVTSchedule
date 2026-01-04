import openpyxl
import re

def get_value_from_merged(sheet, row, col):
    """
    Берет значение, учитывая объединение ячеек в Excel.
    """
    cell = sheet.cell(row, col)
    for merged in sheet.merged_cells.ranges:
        if cell.coordinate in merged:
            return sheet.cell(merged.min_row, merged.min_col).value
    return cell.value

def parse_schedule(file_path):
    """
    Парсер V5 (Adobe Edition).
    Полностью доверяет структуре Excel от Adobe.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    
    schedule_data = []
    
    # --- 1. Поиск шапки ---
    header_row_index = -1
    group_columns = {}
    group_pattern = re.compile(r'^[А-ЯЁ]\d{2}.*') 

    for row_num in range(1, 25):
        for col_num in range(1, sheet.max_column + 1):
            val = sheet.cell(row=row_num, column=col_num).value
            if val and isinstance(val, str):
                val = val.replace('\n', '')
                if group_pattern.match(val.strip()):
                    header_row_index = row_num
                    for c in range(1, sheet.max_column + 1):
                        g_val = sheet.cell(row=row_num, column=c).value
                        if g_val and isinstance(g_val, str) and len(g_val) > 3:
                             group_columns[c] = g_val.strip().replace('\n', '')
                    break
        if header_row_index != -1: break
            
    if header_row_index == -1:
        print(f"⚠️ Шапка не найдена: {file_path}")
        return []

    # --- 2. Чтение данных ---
    current_day = None
    
    for row_num in range(header_row_index + 1, sheet.max_row + 1):
        # А. День недели (с учетом Merged Cells)
        day_val = get_value_from_merged(sheet, row_num, 1)
        if day_val and str(day_val).strip():
            current_day = str(day_val).strip().replace('\n', ' ')
        
        if not current_day: continue

        # Б. Время (с учетом Merged Cells)
        col2_val = get_value_from_merged(sheet, row_num, 2)
        col2_str = str(col2_val).strip().replace('\n', ' ') if col2_val else ""
        
        is_time = False
        # Простая проверка на время (09.00)
        if len(col2_str) < 15 and any(c.isdigit() for c in col2_str):
            is_time = True
        
        if is_time:
            final_time = col2_str
            subject_prefix = ""
        else:
            final_time = "🕒 См. описание" 
            subject_prefix = f"[{col2_str}] " if col2_str and col2_str != "None" else ""

        # В. Проход по группам
        for col_idx, group_name in group_columns.items():
            # Берем значение СТРОГО из ячейки (или её объединения)
            raw_val = get_value_from_merged(sheet, row_num, col_idx)
            
            subject_text = ""
            if raw_val and str(raw_val).strip() and str(raw_val) != "None":
                subject_text = str(raw_val).strip().replace('\n', ' ')
            
            # Если пусто - значит ПУСТО. Не выдумываем.
            if not subject_text:
                continue

            # Финальная обработка времени для экзаменов
            current_final_time = final_time
            if not is_time:
                time_match = re.match(r'(\d{1,2}[:.]\d{2})', subject_text)
                if time_match:
                    current_final_time = time_match.group(1)

            full_subject = f"{subject_prefix}{subject_text}"

            schedule_data.append({
                "day": current_day,
                "time": current_final_time,
                "group": group_name,
                "subject_raw": full_subject
            })

    return schedule_data