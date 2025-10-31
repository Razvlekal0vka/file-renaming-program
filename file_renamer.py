import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path
import threading


class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Программа переименования файлов")
        self.root.geometry("1000x820")
        self.root.resizable(True, True)
        
        # Список пар папок (исходная -> назначение)
        self.folder_pairs = []
        # Индекс пары, которая находится в режиме редактирования (None, если не редактируем)
        self.editing_index = None
        # ID элемента Treeview, который редактируем (для обновления строки)
        self.editing_item_id = None
        
        # Глобальные настройки: разделитель и кавычки для имен
        self.separator_var = tk.StringVar(value=" + ")
        default_quote = "'" if os.name == 'nt' else '"'
        self.quote_var = tk.StringVar(value=default_quote)
        self.include_root_var = tk.BooleanVar(value=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Стили приложения
        self.is_dark_mode = tk.BooleanVar(value=False)
        self.setup_styles()
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Для таблицы папок
        
        # Заголовок и переключатель темы
        title_container = ttk.Frame(main_frame)
        title_container.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 12))
        title_container.columnconfigure(0, weight=1)
        title_label = ttk.Label(title_container, text="Переименование файлов", 
                               font=("SF Pro Text", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(title_container, text="Тёмная тема", variable=self.is_dark_mode,
                        command=self.toggle_theme).grid(row=0, column=1, sticky=tk.E)
        
        # Фрейм для добавления новой пары папок
        add_frame = ttk.LabelFrame(main_frame, text="Добавить папки для обработки", padding="10", style="Card.TLabelframe")
        add_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        add_frame.columnconfigure(1, weight=1)
        add_frame.columnconfigure(3, weight=1)
        
        # Выбор исходной папки
        ttk.Label(add_frame, text="Исходная папка:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_folder_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.source_folder_var, width=40).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(add_frame, text="Выбрать", 
                  command=self.select_source_folder).grid(row=0, column=2, pady=5)
        
        # Выбор папки назначения
        ttk.Label(add_frame, text="Папка назначения:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.destination_folder_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.destination_folder_var, width=40).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(add_frame, text="Выбрать", 
                  command=self.select_destination_folder).grid(row=1, column=2, pady=5)
        
        # Кнопка создания папки по умолчанию
        self.create_default_btn = ttk.Button(add_frame, text="Создать папку сохранения", 
                  command=self.create_default_destination)
        self.create_default_btn.grid(row=2, column=1, pady=5)
        
        # Кнопка добавления пары папок
        self.add_pair_btn = ttk.Button(add_frame, text="Добавить в список", 
                                     command=self.add_folder_pair, style="Accent.TButton")
        self.add_pair_btn.grid(row=2, column=2, pady=5)
        
        # Кнопка отмены редактирования
        self.cancel_edit_btn = ttk.Button(add_frame, text="Отмена редактирования", 
                                        command=self.cancel_edit)
        self.cancel_edit_btn.grid(row=2, column=3, pady=5)
        self.cancel_edit_btn.config(state='disabled')
        
        # Настройки форматирования имен
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки форматирования имен", padding="10", style="Card.TLabelframe")
        settings_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        ttk.Label(settings_frame, text="Разделитель между названиями папок:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.separator_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5,5), pady=5)
        
        ttk.Label(settings_frame, text="Знак для выделения названия папок в названии:").grid(row=0, column=2, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.quote_var, width=10).grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5,5), pady=5)
        
        # Чекбокс включения имени выбранной папки
        ttk.Checkbutton(settings_frame, text="Включать название выбранной папки в наименование файлов", variable=self.include_root_var).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(4,0))
        
        # Создаем подсказку для кнопки
        self.create_tooltip(self.create_default_btn, 
                           "Создает папку с названием 'Результат переименовывания [название_исходной_папки]' в той же директории, где находится исходная папка")
        
        # Таблица со списком папок
        table_frame = ttk.LabelFrame(main_frame, text="Список папок для обработки", padding="10", style="Card.TLabelframe")
        table_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Создаем Treeview для отображения пар папок
        columns = ('source', 'destination')
        self.folder_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10, style="Modern.Treeview")
        
        # Настройка заголовков
        self.folder_tree.heading('source', text='Исходная папка')
        self.folder_tree.heading('destination', text='Папка назначения')
        
        # Настройка колонок
        self.folder_tree.column('source', width=420, minwidth=220)
        self.folder_tree.column('destination', width=420, minwidth=220)
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.folder_tree.yview, style="Modern.Vertical.TScrollbar")
        self.folder_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение таблицы и скроллбара
        self.folder_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Редактирование по двойному клику
        self.folder_tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Кнопки управления списком
        control_frame = ttk.Frame(table_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(control_frame, text="Удалить выбранное", 
                  command=self.remove_selected_pair).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(control_frame, text="Очистить все", 
                  command=self.clear_all_pairs).pack(side=tk.LEFT, padx=6)
        
        # Информационная область
        info_frame = ttk.LabelFrame(main_frame, text="Информация", padding="10", style="Card.TLabelframe")
        info_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        info_frame.columnconfigure(0, weight=1)
        
        info_text = """Программа переименует файлы, добавив к их именам названия всех родительских папок.
Например, если файл 'е.txt' находится в папке 'а/с/', он будет переименован согласно настройкам форматирования.
По умолчанию формат: '"а" + "с" + е.txt'. Вы можете поменять разделитель и кавычки выше."""
        
        ttk.Label(info_frame, text=info_text, wraplength=750, justify=tk.LEFT).grid(
            row=0, column=0, sticky=(tk.W, tk.E))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='determinate', style="Modern.Horizontal.TProgressbar")
        self.progress.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 4))
        # Прогресс текущей пары
        self.progress_pair = ttk.Progressbar(main_frame, mode='determinate', style="Modern.Horizontal.TProgressbar")
        self.progress_pair.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Кнопка запуска
        self.start_button = ttk.Button(main_frame, text="ЗАПУСТИТЬ ОБРАБОТКУ", 
                                     command=self.start_renaming, style="Accent.TButton")
        self.start_button.grid(row=7, column=0, columnspan=4, pady=20)
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к работе")
        self.status_label.grid(row=8, column=0, columnspan=4, pady=5)
        # Детальный прогресс
        self.progress_text = ttk.Label(main_frame, text="")
        self.progress_text.grid(row=9, column=0, columnspan=4, pady=(0,5))

        # Подготовка чередующихся строк
        self.folder_tree.tag_configure('oddrow', background=self._get_color('table_row_alt'))
        self.folder_tree.tag_configure('evenrow', background=self._get_color('table_row'))
        self.refresh_treeview_stripes()

    def setup_styles(self):
        style = ttk.Style()
        # Базовая тема
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # ПАЛИТРЫ
        if self.is_dark_mode.get() if hasattr(self, 'is_dark_mode') else False:
            self.palette = {
                'bg': '#1f1f23',
                'fg': '#f5f7fa',
                'muted': '#c7c9cc',
                'primary': '#5b8def',
                'primary_hover': '#4a7be0',
                'border': '#2d2f36',
                'surface': '#2a2d34',
                'table_row': '#24262b',
                'table_row_alt': '#202228'
            }
        else:
            self.palette = {
                'bg': '#f7f8fa',
                'fg': '#1f2328',
                'muted': '#424a53',
                'primary': '#2563eb',
                'primary_hover': '#1d4ed8',
                'border': '#d0d7de',
                'surface': '#ffffff',
                'table_row': '#ffffff',
                'table_row_alt': '#f3f4f6'
            }

        # Глобальные цвета
        self.root.configure(background=self.palette['bg'])

        # Общие стили
        style.configure('TFrame', background=self.palette['bg'])
        style.configure('TLabelframe', background=self.palette['bg'], foreground=self.palette['fg'])
        style.configure('TLabelframe.Label', foreground=self.palette['fg'])
        style.configure('Card.TLabelframe', background=self.palette['bg'], foreground=self.palette['fg'], bordercolor=self.palette['bg'], borderwidth=0, relief='flat')
        style.configure('Card.TLabelframe.Label', background=self.palette['bg'], foreground=self.palette['muted'])
        style.configure('TLabel', background=self.palette['bg'], foreground=self.palette['fg'], font=("SF Pro Text", 11))
        style.configure('TEntry', fieldbackground=self.palette['surface'], foreground=self.palette['fg'], bordercolor=self.palette['surface'], lightcolor=self.palette['surface'], darkcolor=self.palette['surface'])
        style.map('TEntry', fieldbackground=[('disabled', self.palette['surface'])])

        # Кнопки
        style.configure('TButton', font=("SF Pro Text", 11), padding=8, relief='flat', borderwidth=0)
        style.map('TButton', foreground=[('active', self.palette['fg'])])
        style.configure('Accent.TButton', background=self.palette['primary'], foreground='#ffffff', relief='flat', borderwidth=0)
        style.map('Accent.TButton', background=[('active', self.palette['primary_hover'])])

        # Прогрессбар
        style.configure('Modern.Horizontal.TProgressbar', troughcolor=self.palette['surface'], background=self.palette['primary'], bordercolor=self.palette['border'], lightcolor=self.palette['primary'], darkcolor=self.palette['primary'])

        # Таблица
        style.configure('Modern.Treeview', background=self.palette['surface'], fieldbackground=self.palette['surface'], foreground=self.palette['fg'], rowheight=28, bordercolor=self.palette['bg'], borderwidth=0)
        style.configure('Treeview.Heading', background=self.palette['bg'], foreground=self.palette['muted'], font=("SF Pro Text", 11, 'bold'), bordercolor=self.palette['bg'], relief='flat')
        style.map('Treeview.Heading', background=[('active', self.palette['bg'])])

        # Скроллбар
        style.configure('Modern.Vertical.TScrollbar', gripcount=0, background=self.palette['surface'], darkcolor=self.palette['bg'], lightcolor=self.palette['bg'], troughcolor=self.palette['bg'], bordercolor=self.palette['bg'], arrowcolor=self.palette['muted'])

    def _get_color(self, key):
        return self.palette.get(key)

    def toggle_theme(self):
        # Переключение темы и обновление стилей/расцветки
        self.setup_styles()
        # Обновляем цвета тегов таблицы
        self.folder_tree.tag_configure('oddrow', background=self._get_color('table_row_alt'))
        self.folder_tree.tag_configure('evenrow', background=self._get_color('table_row'))
        self.refresh_treeview_stripes()

    def refresh_treeview_stripes(self):
        # Чередование цветов строк
        for index, item_id in enumerate(self.folder_tree.get_children()):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.folder_tree.item(item_id, tags=(tag,))

    def _invalid_filename_chars(self):
        return '<>:"/\\|?*' if os.name == 'nt' else '/'

    def _sanitize_option(self, value, fallback=""):
        if value is None:
            value = ""
        invalid_chars = self._invalid_filename_chars()
        sanitized = ''.join(ch for ch in value if ch not in invalid_chars)
        if sanitized:
            return sanitized
        return fallback

    def _effective_separator(self, separator):
        sanitized = self._sanitize_option(separator, fallback="")
        if not sanitized and separator:
            # Если пользователь указал только запрещенные символы, используем безопасный дефолт
            return "_"
        return sanitized

    def _effective_quote(self, quote):
        fallback = "'" if os.name == 'nt' else ""
        sanitized = self._sanitize_option(quote, fallback=fallback)
        return sanitized

    def _sanitize_output_name(self, name):
        if name is None:
            return "_"
        invalid_chars = self._invalid_filename_chars()
        sanitized = ''.join(ch for ch in name if ch not in invalid_chars and ch != '\0')
        sanitized = sanitized.strip()
        if os.name == 'nt':
            sanitized = sanitized.rstrip('. ')
        return sanitized or "_"
    
    def create_tooltip(self, widget, text):
        """Создает подсказку для виджета"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="lightyellow", 
                            relief="solid", borderwidth=1, padding="5")
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Выберите исходную папку")
        if folder:
            self.source_folder_var.set(folder)
            self.status_label.config(text="Исходная папка выбрана")
    
    def select_destination_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку назначения")
        if folder:
            self.destination_folder_var.set(folder)
            self.status_label.config(text="Папка назначения выбрана")
    
    def create_default_destination(self):
        if not self.source_folder_var.get():
            messagebox.showwarning("Предупреждение", "Сначала выберите исходную папку!")
            return
        
        source_path = Path(self.source_folder_var.get())
        parent_dir = source_path.parent
        default_name = "Результат переименовывания " + source_path.name
        default_path = parent_dir / default_name
        
        self.destination_folder_var.set(str(default_path))
        self.status_label.config(text="Папка назначения установлена по умолчанию")
    
    def add_folder_pair(self):
        """Добавляет пару папок в список для обработки"""
        source = self.source_folder_var.get().strip()
        destination = self.destination_folder_var.get().strip()
        
        if not source or not destination:
            messagebox.showwarning("Предупреждение", "Выберите обе папки!")
            return
        
        if not os.path.exists(source):
            messagebox.showerror("Ошибка", "Исходная папка не существует!")
            return
        
        # Проверяем, не добавлена ли уже такая пара
        for pair in self.folder_pairs:
            if pair['source'] == source:
                messagebox.showwarning("Предупреждение", "Эта исходная папка уже добавлена в список!")
                return
        
        # Добавляем пару в список
        pair = {'source': source, 'destination': destination}
        self.folder_pairs.append(pair)
        
        # Добавляем в таблицу
        new_id = self.folder_tree.insert('', 'end', values=(source, destination))
        self.refresh_treeview_stripes()
        
        # Очищаем поля ввода
        self.source_folder_var.set("")
        self.destination_folder_var.set("")
        
        self.status_label.config(text=f"Добавлено в список. Всего пар: {len(self.folder_pairs)}")
    
    def remove_selected_pair(self):
        """Удаляет выбранную пару папок из списка"""
        selected = self.folder_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пару для удаления!")
            return
        
        # Получаем индекс выбранного элемента
        item = self.folder_tree.item(selected[0])
        source = item['values'][0]
        
        # Удаляем из списка
        self.folder_pairs = [pair for pair in self.folder_pairs if pair['source'] != source]
        
        # Удаляем из таблицы
        self.folder_tree.delete(selected[0])
        self.refresh_treeview_stripes()
        
        self.status_label.config(text=f"Пара удалена. Всего пар: {len(self.folder_pairs)}")
    
    def clear_all_pairs(self):
        """Очищает весь список пар папок"""
        if not self.folder_pairs:
            messagebox.showinfo("Информация", "Список уже пуст!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить весь список?"):
            self.folder_pairs.clear()
            for item in self.folder_tree.get_children():
                self.folder_tree.delete(item)
            self.refresh_treeview_stripes()
            self.status_label.config(text="Список очищен")
    
    def on_tree_double_click(self, event):
        """Переводит выбранную пару в режим редактирования и подставляет значения в поля"""
        item_id = self.folder_tree.identify_row(event.y)
        if not item_id:
            return
        values = self.folder_tree.item(item_id, 'values')
        if not values:
            return
        source, destination = values[0], values[1]
        
        # Находим индекс пары по source
        pair_index = None
        for i, pair in enumerate(self.folder_pairs):
            if pair['source'] == source and pair['destination'] == destination:
                pair_index = i
                break
        if pair_index is None:
            return
        
        # Входим в режим редактирования
        self.editing_index = pair_index
        self.editing_item_id = item_id
        self.source_folder_var.set(source)
        self.destination_folder_var.set(destination)
        self.add_pair_btn.config(text="Сохранить изменения", command=self.save_edit_pair)
        self.cancel_edit_btn.config(state='normal')
        self.status_label.config(text="Режим редактирования пары")

    def save_edit_pair(self):
        """Сохраняет изменения текущей редактируемой пары из полей ввода"""
        if self.editing_index is None:
            return
        new_source = self.source_folder_var.get().strip()
        new_destination = self.destination_folder_var.get().strip()
        
        if not new_source or not new_destination:
            messagebox.showwarning("Предупреждение", "Укажите обе папки!")
            return
        if not os.path.exists(new_source):
            messagebox.showerror("Ошибка", "Исходная папка не существует!")
            return
        
        # Проверяем дубликаты по source среди других пар
        for i, pair in enumerate(self.folder_pairs):
            if i != self.editing_index and pair['source'] == new_source:
                messagebox.showwarning("Предупреждение", "Эта исходная папка уже есть в списке!")
                return
        
        # Обновляем данные
        self.folder_pairs[self.editing_index]['source'] = new_source
        self.folder_pairs[self.editing_index]['destination'] = new_destination
        
        # Обновляем строку таблицы
        if self.editing_item_id:
            self.folder_tree.item(self.editing_item_id, values=(new_source, new_destination))
        
        # Выходим из режима редактирования
        self.source_folder_var.set("")
        self.destination_folder_var.set("")
        self.add_pair_btn.config(text="Добавить в список", command=self.add_folder_pair)
        self.cancel_edit_btn.config(state='disabled')
        self.status_label.config(text="Изменения сохранены")
        self.editing_index = None
        self.editing_item_id = None

    def cancel_edit(self):
        """Отмена режима редактирования без сохранения"""
        self.editing_index = None
        self.editing_item_id = None
        self.source_folder_var.set("")
        self.destination_folder_var.set("")
        self.add_pair_btn.config(text="Добавить в список", command=self.add_folder_pair)
        self.cancel_edit_btn.config(state='disabled')
        self.status_label.config(text="Редактирование отменено")
    
    def open_edit_dialog(self, pair_index, item_id):
        """Окно редактирования папки назначения для выбранной пары"""
        pair = self.folder_pairs[pair_index]
        source_path = pair['source']
        dest_var = tk.StringVar(value=pair['destination'])
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование параметров сохранения")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="Исходная папка:").grid(row=0, column=0, sticky=tk.W, pady=(0,5))
        ttk.Label(frame, text=source_path, wraplength=500).grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0,5))
        
        ttk.Label(frame, text="Папка назначения:").grid(row=1, column=0, sticky=tk.W)
        dest_entry = ttk.Entry(frame, textvariable=dest_var, width=60)
        dest_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5,5))
        
        def choose_dest():
            folder = filedialog.askdirectory(title="Выберите папку назначения")
            if folder:
                dest_var.set(folder)
        ttk.Button(frame, text="Выбрать", command=choose_dest).grid(row=1, column=2)
        
        def set_default():
            source = Path(source_path)
            parent_dir = source.parent
            default_name = "Результат переименовывания " + source.name
            dest_var.set(str(parent_dir / default_name))
        ttk.Button(frame, text="Установить по умолчанию", command=set_default).grid(row=2, column=1, sticky=tk.W, pady=(8,0))
        
        btns = ttk.Frame(frame)
        btns.grid(row=3, column=0, columnspan=3, pady=12)
        
        def save_and_close():
            new_dest = dest_var.get().strip()
            if not new_dest:
                messagebox.showwarning("Предупреждение", "Папка назначения не может быть пустой!", parent=dialog)
                return
            self.folder_pairs[pair_index]['destination'] = new_dest
            # Обновляем строку в таблице
            self.folder_tree.item(item_id, values=(source_path, new_dest))
            self.status_label.config(text="Параметры сохранены")
            dialog.destroy()
        
        ttk.Button(btns, text="Сохранить", command=save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def start_renaming(self):
        if not self.folder_pairs:
            messagebox.showerror("Ошибка", "Добавьте хотя бы одну пару папок для обработки!")
            return
        
        # Запуск в отдельном потоке
        self.start_button.config(state='disabled')
        # Подсчет файлов заранее
        total_files = 0
        pair_file_counts = []
        for pair in self.folder_pairs:
            src = Path(pair['source'])
            count = self.count_files_in_dir(src) if src.exists() else 0
            pair_file_counts.append(count)
            total_files += count

        self.total_files = total_files
        self.processed_files = 0
        self.pair_file_counts = pair_file_counts
        self.current_pair_index = -1

        # Настройка прогресс-баров
        self.progress.config(maximum=max(1, self.total_files))
        self.progress['value'] = 0
        self.progress_pair.config(maximum=1)
        self.progress_pair['value'] = 0
        self.status_label.config(text="Обработка...")
        self.progress_text.config(text=f"0 / {self.total_files} файлов (0%)")
        
        thread = threading.Thread(target=self.rename_files)
        thread.daemon = True
        thread.start()
    
    def rename_files(self):
        try:
            total_renamed = 0
            processed_pairs = 0
            
            for i, pair in enumerate(self.folder_pairs):
                try:
                    source_path = Path(pair['source'])
                    dest_path = Path(pair['destination'])
                    
                    # Обновляем статус
                    self.root.after(0, self.update_status, f"Обработка папки {i+1} из {len(self.folder_pairs)}: {source_path.name}")
                    self.current_pair_index = i
                    pair_total = self.pair_file_counts[i] if i < len(self.pair_file_counts) else 0
                    self.root.after(0, self.reset_pair_progress, max(1, pair_total))
                    
                    # Удаляем папку назначения если существует
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    
                    # Копируем всю структуру папок
                    if source_path.exists():
                        shutil.copytree(source_path, dest_path)
                    
                    # Переименовываем файлы
                    renamed_count = self.rename_files_recursive(
                        dest_path, dest_path,
                        separator=self.separator_var.get(),
                        quote=self.quote_var.get(),
                        include_root=self.include_root_var.get(),
                        root_name=source_path.name,
                        on_file_processed=lambda rel: self.root.after(0, self.increment_progress, rel)
                    )
                    total_renamed += renamed_count
                    processed_pairs += 1
                    
                    # Обновляем прогресс
                    # Завершение прогресса пары
                    self.root.after(0, self.finish_pair_progress)
                    
                except Exception as e:
                    print(f"Ошибка при обработке пары {pair['source']} -> {pair['destination']}: {e}")
                    continue
            
            # Обновляем UI в главном потоке
            self.root.after(0, self.rename_complete, total_renamed, processed_pairs)
            
        except Exception as e:
            self.root.after(0, self.rename_error, str(e))
    
    def rename_files_recursive(self, current_path, root_path, total_renamed=0, separator=" + ", quote='"', include_root=False, root_name=None, on_file_processed=None):
        files_in_this_dir = 0
        safe_quote = self._effective_quote(quote or '')
        safe_separator = self._effective_separator(separator or '')
        
        for item in current_path.iterdir():
            if item.is_file():
                files_in_this_dir += 1
                # Получаем относительный путь от корневой папки
                relative_path = item.relative_to(root_path)
                
                # Создаем новое имя файла из названий папок
                folder_names = [part for part in relative_path.parts[:-1]]  # Все части кроме имени файла
                if include_root and root_name:
                    folder_names = [root_name] + folder_names
                file_name = item.stem  # Имя файла без расширения
                file_extension = item.suffix  # Расширение файла
                
                # Объединяем названия папок с пользовательскими параметрами
                components = []
                if folder_names:
                    components.extend([f"{safe_quote}{name}{safe_quote}" if safe_quote else name for name in folder_names])
                components.append(file_name)

                if safe_separator:
                    base_name = safe_separator.join(components)
                else:
                    base_name = ''.join(components)

                sanitized_base = self._sanitize_output_name(base_name)
                new_name = f"{sanitized_base}{file_extension}"
                
                # Переименовываем файл
                new_path = item.parent / new_name
                
                if str(new_path) != str(item):  # Избегаем переименования в то же имя
                    try:
                        item.rename(new_path)
                        total_renamed += 1
                        if on_file_processed is not None:
                            try:
                                on_file_processed(str(relative_path))
                            except Exception:
                                pass
                    except Exception as e:
                        print(f"Ошибка переименования {item} в {new_path}: {e}")
                    
            elif item.is_dir():
                # Рекурсивно обрабатываем подпапки
                total_renamed = self.rename_files_recursive(
                    item, root_path, total_renamed,
                    separator=safe_separator, quote=safe_quote,
                    include_root=include_root, root_name=root_name,
                    on_file_processed=on_file_processed
                )
        
        return total_renamed
    
    def update_status(self, message):
        """Обновляет статус в главном потоке"""
        self.status_label.config(text=message)
    
    def update_progress(self, value):
        """Обновляет прогресс-бар в главном потоке"""
        self.progress['value'] = value

    def reset_pair_progress(self, pair_total):
        self.progress_pair.config(maximum=max(1, pair_total))
        self.progress_pair['value'] = 0

    def finish_pair_progress(self):
        self.progress_pair['value'] = self.progress_pair['maximum']

    def increment_progress(self, relative_path):
        # Обновляем суммарный прогресс
        self.processed_files = min(self.total_files, self.processed_files + 1)
        self.progress['value'] = self.processed_files
        # Обновляем прогресс текущей пары
        self.progress_pair['value'] = min(self.progress_pair['maximum'], self.progress_pair['value'] + 1)
        # Обновляем текст
        percent = 0 if self.total_files == 0 else int(self.processed_files * 100 / self.total_files)
        # Укорачиваем путь для отображения
        disp = relative_path
        if len(disp) > 60:
            disp = '…' + disp[-59:]
        self.progress_text.config(text=f"{self.processed_files} / {self.total_files} файлов ({percent}%) — {disp}")

    def count_files_in_dir(self, directory: Path) -> int:
        total = 0
        try:
            for root, dirs, files in os.walk(directory):
                total += len(files)
        except Exception:
            pass
        return total
    
    def rename_complete(self, renamed_count, processed_pairs):
        self.progress['value'] = self.total_files if hasattr(self, 'total_files') else len(self.folder_pairs)
        self.finish_pair_progress()
        self.start_button.config(state='normal')
        self.status_label.config(text="Готово! Обработка завершена")
        self.progress_text.config(text=f"Переименовано файлов: {renamed_count}")
        messagebox.showinfo("Успех", "Успешно переименовано")
    
    def rename_error(self, error_message):
        self.progress['value'] = 0
        self.start_button.config(state='normal')
        self.status_label.config(text="Ошибка при обработке")
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{error_message}")


def main():
    root = tk.Tk()
    
    # Настройка стиля
    style = ttk.Style()
    style.theme_use('clam')
    
    # Создание приложения
    app = FileRenamerApp(root)
    
    # Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()
