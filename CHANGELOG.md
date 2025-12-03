# Changelog / История изменений

All notable changes to this project will be documented in this file.
Все значимые изменения в проекте документируются в этом файле.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

## [1.2.0] - 2025-01-XX

### Added / Добавлено
- Flatten structure mode: option to save all files in a single folder
- Режим плоской структуры: опция сохранения всех файлов в одну папку
- Automatic name conflict resolution with numbered suffixes (_1, _2, etc.)
- Автоматическое разрешение конфликтов имен с нумерованными суффиксами (_1, _2 и т.д.)
- Warning dialog when enabling flatten mode
- Диалог предупреждения при включении режима плоской структуры

### Changed / Изменено
- Added checkbox to toggle between structure preservation and flatten mode
- Добавлен чекбокс для переключения между сохранением структуры и режимом плоской структуры
- Improved file processing flexibility with two distinct modes
- Улучшена гибкость обработки файлов с двумя различными режимами

### Features / Функции
- **Structure Mode** (default): Preserves folder hierarchy, renames files in place
- **Режим структуры** (по умолчанию): Сохраняет иерархию папок, переименовывает файлы на месте
- **Flatten Mode**: Copies all files to a single folder with new names, handles conflicts automatically
- **Режим плоской структуры**: Копирует все файлы в одну папку с новыми именами, автоматически обрабатывает конфликты

## [1.1.0] - 2025-01-XX

### Added / Добавлено
- Performance optimizations for large file batches
- Оптимизации производительности для больших пакетов файлов
- Optimized file renaming algorithm using os.walk()
- Оптимизированный алгоритм переименования файлов с использованием os.walk()
- Batch UI updates to reduce GUI overhead
- Батчинг обновлений UI для снижения нагрузки на GUI
- PyInstaller spec file for building standalone executables
- Файл spec PyInstaller для сборки автономных исполняемых файлов
- Comprehensive technical documentation (SPEC.md)
- Подробная техническая документация (SPEC.md)

### Changed / Изменено
- Improved file processing speed (2-5x faster for large batches)
- Улучшена скорость обработки файлов (в 2-5 раз быстрее для больших пакетов)
- UI updates now batched instead of per-file
- Обновления UI теперь батчируются вместо обновления для каждого файла
- More efficient directory traversal algorithm
- Более эффективный алгоритм обхода директорий

### Performance / Производительность
- Reduced GUI overhead by 90%+ through batched updates
- Снижена нагрузка на GUI на 90%+ благодаря батчированным обновлениям
- Faster file processing using os.walk() instead of recursive Path.iterdir()
- Быстрая обработка файлов с использованием os.walk() вместо рекурсивного Path.iterdir()
- Optimized string operations and filename formatting
- Оптимизированы строковые операции и форматирование имен файлов

## [1.0.0] - 2025-01-XX

### Added / Добавлено
- Initial release of the file renaming application
- Первый релиз приложения для переименования файлов
- GUI interface built with tkinter
- Графический интерфейс на основе tkinter
- Support for multiple folder pairs processing
- Поддержка обработки нескольких пар папок
- Configurable separator and quote symbols for file naming
- Настраиваемые разделитель и кавычки для именования файлов
- Option to include root folder name in file names
- Опция включения имени корневой папки в имена файлов
- Progress tracking with dual progress bars
- Отслеживание прогресса с двумя прогресс-барами
- Dark and light theme support
- Поддержка темной и светлой тем
- Windows filename sanitization to prevent WinError 123
- Очистка имен файлов для Windows для предотвращения WinError 123
- Automatic default destination folder creation
- Автоматическое создание папки назначения по умолчанию
- Folder pair editing with double-click
- Редактирование пар папок по двойному клику

### Fixed / Исправлено
- Windows filename validation errors (WinError 123)
- Ошибки валидации имен файлов в Windows (WinError 123)
- Invalid characters in filenames are now sanitized
- Запрещенные символы в именах файлов теперь очищаются
- Proper handling of quotes and separators on Windows
- Корректная обработка кавычек и разделителей в Windows

### Security / Безопасность
- Path sanitization to prevent directory traversal
- Очистка путей для предотвращения обхода директорий
- Safe filename generation with character filtering
- Безопасная генерация имен файлов с фильтрацией символов

