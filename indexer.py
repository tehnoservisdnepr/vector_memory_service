import os
import glob
import docx
from sentence_transformers import SentenceTransformer

PROCESSED_LOG = "processed_files.txt"
IGNORE_LIST_FILE = "ignore_list.txt"

def load_processed_files():
    if not os.path.exists(PROCESSED_LOG):
        return set()
    with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def load_ignored_files():
    ignored = set()
    if os.path.exists(IGNORE_LIST_FILE):
        with open(IGNORE_LIST_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    ignored.add(line.strip())
    return ignored

def mark_as_processed(filename):
    with open(PROCESSED_LOG, "a", encoding="utf-8") as f:
        f.write(filename + "\n")

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        if para.text.strip():
            fullText.append(para.text.strip())
    return fullText

def main():
    print("Инициализация поискового модуля...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Загружаем списки
    processed_files = load_processed_files()
    ignored_files = load_ignored_files()
    
    # Получаем список всех поддерживаемых файлов в текущей директории
    all_files = [f for f in os.listdir(".") if f.endswith(".docx")]
    
    # Фильтруем: исключаем уже обработанные И файлы из черного списка
    files_to_process = [
        f for f in all_files 
        if f not in processed_files and f not in ignored_files
    ]
    
    print(f"Найдено документов всего: {len(all_files)}")
    print(f"Уже в базе (пропущены): {len(processed_files)}")
    print(f"В игнор-листе (пропущены): {len(ignored_files)}")
    print(f"К индексации: {len(files_to_process)}")

    if not files_to_process:
        print("Все подходящие файлы уже заиндексированы. Работы нет!")
        return

    for filename in files_to_process:
        print(f"\n--- Обработка документа: {filename} ---")
        
        try:
            paragraphs = extract_text_from_docx(filename)
            print(f"Найдено абзацев: {len(paragraphs)}")

            if paragraphs:
                embeddings = model.encode(paragraphs, show_progress_bar=True)
                print(f"Успешно сгенерировано векторов: {len(embeddings)}")
                # Здесь в будущем сохраним векторы в базу/файл для быстрого поиска

            mark_as_processed(filename)
            print(f"--- Успешно заиндексирован и сохранен в реестр: {filename} ---")
            
        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {e}")

if __name__ == "__main__":
    main()