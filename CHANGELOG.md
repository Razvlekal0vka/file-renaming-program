# Changelog / История изменений

All notable changes to this project will be documented in this file.
Все значимые изменения в проекте документируются в этом файле.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

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

