import os

# Настройки
project_root = '.'  # текущая директория — корень проекта
output_file = 'project_summary.txt'

# Что игнорировать
ignore_dirs = ['venv', '__pycache__', '.git', 'node_modules', '.venv', '.vscode']
ignore_files = ['.pyc', '.log', '.jpg', '.png', '.exe', '.DS_Store', '.ico']

def is_text_file(filename):
    """Проверяет, является ли файл текстовым."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except UnicodeDecodeError:
        return False
    except Exception:
        return False

def collect_project_files(root_dir):
    collected_content = ""
    for root, dirs, files in os.walk(root_dir):
        # Убираем ненужные папки
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            file_path = os.path.join(root, file)

            # Пропустить игнорируемые расширения
            if any(file.endswith(ext) for ext in ignore_files):
                continue

            if is_text_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    relative_path = os.path.relpath(file_path, root_dir)
                    collected_content += f"{'='*80}\n"
                    collected_content += f"File: {relative_path}\n"
                    collected_content += f"{'-'*80}\n"
                    collected_content += content + "\n\n"
                except Exception as e:
                    print(f"[ERROR] Can't read file {file_path}: {e}")
    return collected_content

if __name__ == '__main__':
    print("Сборка проекта в один файл...")
    content = collect_project_files(project_root)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Проект успешно собран в файл: {output_file}")