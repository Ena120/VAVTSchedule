import os
import json
import logging
import time # <--- Добавили импорт времени

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.export_pdf_job import ExportPDFJob
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_params import ExportPDFParams
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_target_format import ExportPDFTargetFormat
from adobe.pdfservices.operation.pdfjobs.result.export_pdf_result import ExportPDFResult
from adobe.pdfservices.operation.config.client_config import ClientConfig

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

def convert_pdf_to_xlsx(input_pdf_path, output_xlsx_path):
    print(f"🔄 [Adobe API] Начинаю конвертацию: {input_pdf_path}")
    
    # Пытаемся 3 раза, если ошибка сети
    max_retries = 3
    
    for attempt in range(1, max_retries + 1):
        try:
            base_path = os.getcwd()
            key_file = os.path.join(base_path, "pdfservices-api-credentials.json")
            
            if not os.path.exists(key_file):
                print(f"❌ Ошибка: Файл ключей не найден: {key_file}")
                return False
                
            with open(key_file, "r") as f:
                config = json.load(f)
                
            client_id = config.get("client_credentials", {}).get("client_id") or config.get("client_id")
            client_secret = config.get("client_credentials", {}).get("client_secret") or config.get("client_secret")

            if not client_id or not client_secret:
                raise ValueError("❌ Не найдены ключи в JSON файле")

            credentials = ServicePrincipalCredentials(
                client_id=client_id,
                client_secret=client_secret
            )

            # Тайм-ауты (увеличенные)
            client_config = ClientConfig(connect_timeout=60000, read_timeout=300000)
            pdf_services = PDFServices(credentials=credentials, client_config=client_config)

            with open(input_pdf_path, 'rb') as file_stream:
                if attempt == 1:
                    print("☁️  Загружаю файл на сервер Adobe...")
                else:
                    print(f"🔄 Попытка {attempt}/{max_retries}...")

                input_asset = pdf_services.upload(file_stream, PDFServicesMediaType.PDF.value)
                
                export_pdf_params = ExportPDFParams(target_format=ExportPDFTargetFormat.XLSX)
                export_pdf_job = ExportPDFJob(input_asset, export_pdf_params)

                # print("⏳ Конвертация...") 
                polling_url = pdf_services.submit(export_pdf_job)
                
                pdf_services_response = pdf_services.get_job_result(polling_url, ExportPDFResult)
                export_result = pdf_services_response.get_result()
                
                if export_result:
                    result_asset = export_result.get_asset()
                    # print("💾 Скачиваю...")
                    
                    stream_asset = pdf_services.get_content(result_asset)
                    
                    with open(output_xlsx_path, "wb") as file:
                        file.write(stream_asset.get_input_stream())
                    
                    print(f"✅ Успешно! Файл сохранен: {output_xlsx_path}")
                    return True # Выходим из цикла и функции при успехе
                else:
                    print("❌ Adobe вернул пустой результат.")
                    # Если пустой результат - это не ошибка сети, повторять смысла мало, но можно попробовать
                    
        except Exception as e:
            print(f"⚠️ Ошибка при попытке {attempt}: {e}")
            if attempt < max_retries:
                print("⏳ Жду 5 секунд и пробую снова...")
                time.sleep(5)
            else:
                print("❌ Не удалось сконвертировать файл после 3 попыток.")
                return False
    
    return False