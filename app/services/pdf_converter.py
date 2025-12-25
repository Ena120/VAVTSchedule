import os
import json
import logging
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
    print(f"🔄 [Adobe V4] Начинаю конвертацию: {input_pdf_path}")
    
    try:
        # 1. Читаем ключи
        base_path = os.getcwd()
        key_file = os.path.join(base_path, "pdfservices-api-credentials.json")
        
        with open(key_file, "r") as f:
            config = json.load(f)
            
        client_id = config.get("client_credentials", {}).get("client_id") or config.get("client_id")
        client_secret = config.get("client_credentials", {}).get("client_secret") or config.get("client_secret")

        if not client_id or not client_secret:
            raise ValueError("❌ Не найдены ключи в pdfservices-api-credentials.json")

        # 2. Авторизация
        credentials = ServicePrincipalCredentials(
            client_id=client_id,
            client_secret=client_secret
        )

        # 3. Настройка тайм-аута (1 минута)
        client_config = ClientConfig(connect_timeout=10000, read_timeout=60000)

        # 4. Создаем сервис
        pdf_services = PDFServices(credentials=credentials, client_config=client_config)

        # 5. Загружаем и отправляем
        with open(input_pdf_path, 'rb') as file_stream:
            print("☁️ Загружаю файл в Adobe Cloud...")
            input_asset = pdf_services.upload(file_stream, PDFServicesMediaType.PDF.value)
            
            export_pdf_params = ExportPDFParams(target_format=ExportPDFTargetFormat.XLSX)
            export_pdf_job = ExportPDFJob(input_asset, export_pdf_params)

            print("⏳ Конвертирую...")
            polling_url = pdf_services.submit(export_pdf_job)
            
            pdf_services_response = pdf_services.get_job_result(polling_url, ExportPDFResult)
            export_result = pdf_services_response.get_result()
            
            # 6. Скачиваем и сохраняем (ИСПРАВЛЕНО)
            if export_result:
                result_asset = export_result.get_asset()
                print("💾 Скачиваю результат...")
                
                stream_asset = pdf_services.get_content(result_asset)
                
                # ВОТ ЗДЕСЬ БЫЛА ОШИБКА. ТЕПЕРЬ ПРАВИЛЬНО:
                with open(output_xlsx_path, "wb") as file:
                    file.write(stream_asset.get_input_stream())
                
                print(f"✅ Успешно! Файл сохранен: {output_xlsx_path}")
                return True
            else:
                print("❌ Adobe вернул пустой результат")
                return False

    except Exception as e:
        print(f"❌ Ошибка Adobe API: {e}")
        return False