from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QLabel, QDialog, QWidget, QMessageBox, QInputDialog
)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fpdf import FPDF

# SQLAlchemy: создание модели и подключение к MySQL
Base = declarative_base()
# Диалог редактирования книги
class EditBookDialog(QDialog):
    def __init__(self, session, parent=None, book=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать книгу")
        self.session = session
        self.book = book

        self.layout = QVBoxLayout()

        # Поля для редактирования
        self.title_input = QLineEdit(self.book.title)
        self.author_input = QLineEdit(self.book.author)
        self.year_input = QLineEdit(str(self.book.year) if self.book.year else "")
        self.genre_input = QLineEdit(self.book.genre if self.book.genre else "")

        self.layout.addWidget(QLabel("Название"))
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(QLabel("Автор"))
        self.layout.addWidget(self.author_input)
        self.layout.addWidget(QLabel("Год"))
        self.layout.addWidget(self.year_input)
        self.layout.addWidget(QLabel("Жанр"))
        self.layout.addWidget(self.genre_input)

        # Кнопка для сохранения изменений
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_changes(self):
        """Сохранение изменений в книге."""
        self.book.title = self.title_input.text()
        self.book.author = self.author_input.text()
        self.book.year = int(self.year_input.text()) if self.year_input.text().isdigit() else None
        self.book.genre = self.genre_input.text()

        # Сохранение изменений в базе данных
        self.session.commit()
        self.accept()


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    genre = Column(String, nullable=True)


# Подключение к MySQL
DATABASE_URL = "mysql+pymysql://root:Qwerty@localhost:3306/books_db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
# Диалог добавления книги
class AddBookDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить книгу")
        self.session = session

        # Основной макет
        self.layout = QVBoxLayout()

        # Поля для ввода данных
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QLineEdit()
        self.genre_input = QLineEdit()

        self.layout.addWidget(QLabel("Название"))
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(QLabel("Автор"))
        self.layout.addWidget(self.author_input)
        self.layout.addWidget(QLabel("Год"))
        self.layout.addWidget(self.year_input)
        self.layout.addWidget(QLabel("Жанр"))
        self.layout.addWidget(self.genre_input)

        # Кнопка для сохранения
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.save_book)
        self.layout.addWidget(self.add_button)

        # Установка макета
        self.setLayout(self.layout)

    def save_book(self):
        """Сохранение новой книги в базу данных."""
        new_book = Book(
            title=self.title_input.text(),
            author=self.author_input.text(),
            year=int(self.year_input.text()) if self.year_input.text().isdigit() else None,
            genre=self.genre_input.text()
        )
        self.session.add(new_book)
        self.session.commit()
        self.accept()


# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Библиотека книг")
        self.resize(800, 600)

        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Основной макет
        self.layout = QVBoxLayout()

        # Таблица для отображения книг
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Год", "Жанр"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.table)

        # Панель кнопок
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")
        self.search_button = QPushButton("Поиск")
        self.filter_button = QPushButton("Фильтрация")
        self.report_button = QPushButton("Генерация отчета")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.filter_button)
        button_layout.addWidget(self.report_button)

        self.layout.addLayout(button_layout)
        self.central_widget.setLayout(self.layout)

        # Обработчики событий
        self.add_button.clicked.connect(self.add_book)
        self.edit_button.clicked.connect(self.edit_book)
        self.delete_button.clicked.connect(self.delete_book)
        self.search_button.clicked.connect(self.search_book)
        self.filter_button.clicked.connect(self.filter_books)
        self.report_button.clicked.connect(self.generate_report)

        # Загрузка данных
        self.load_data()

    def load_data(self):
        """Загрузка данных из базы данных и отображение в таблице."""
        books = session.query(Book).all()
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            self.table.setItem(row, 0, QTableWidgetItem(str(book.id)))
            self.table.setItem(row, 1, QTableWidgetItem(book.title))
            self.table.setItem(row, 2, QTableWidgetItem(book.author))
            self.table.setItem(row, 3, QTableWidgetItem(str(book.year)))
            self.table.setItem(row, 4, QTableWidgetItem(book.genre))

    def add_book(self):
        """Окно добавления книги."""
        dialog = AddBookDialog(session, self)
        if dialog.exec():
            self.load_data()

    def edit_book(self):
        """Редактирование выбранной книги."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для редактирования")
            return

        book_id = int(self.table.item(selected_row, 0).text())
        book = session.query(Book).get(book_id)
        dialog = EditBookDialog(session, self, book)
        if dialog.exec():
            self.load_data()

    def delete_book(self):
        """Удаление выбранной книги."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления")
            return

        book_id = int(self.table.item(selected_row, 0).text())
        book = session.query(Book).get(book_id)
        session.delete(book)
        session.commit()
        self.load_data()

    def search_book(self):
        """Поиск книги по названию."""
        keyword, ok = QInputDialog.getText(self, "Поиск книги", "Введите название книги:")
        if ok and keyword:
            books = session.query(Book).filter(Book.title.ilike(f"%{keyword}%")).all()
            
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QLabel, QDialog, QWidget, QMessageBox, QInputDialog
)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fpdf import FPDF

# SQLAlchemy: создание модели и подключение к MySQL
Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    genre = Column(String, nullable=True)


# Подключение к MySQL
DATABASE_URL = "mysql+pymysql://root:Qwerty@localhost:3306/books_db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# Диалог добавления книги
class AddBookDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить книгу")
        self.session = session

        self.layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QLineEdit()
        self.genre_input = QLineEdit()

        self.layout.addWidget(QLabel("Название"))
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(QLabel("Автор"))
        self.layout.addWidget(self.author_input)
        self.layout.addWidget(QLabel("Год"))
        self.layout.addWidget(self.year_input)
        self.layout.addWidget(QLabel("Жанр"))
        self.layout.addWidget(self.genre_input)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.save_book)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def save_book(self):
        new_book = Book(
            title=self.title_input.text(),
            author=self.author_input.text(),
            year=int(self.year_input.text()) if self.year_input.text().isdigit() else None,
            genre=self.genre_input.text()
        )
        self.session.add(new_book)
        self.session.commit()
        self.accept()


# Диалог редактирования книги
class EditBookDialog(QDialog):
    def __init__(self, session, parent=None, book=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать книгу")
        self.session = session
        self.book = book

        self.layout = QVBoxLayout()

        self.title_input = QLineEdit(self.book.title)
        self.author_input = QLineEdit(self.book.author)
        self.year_input = QLineEdit(str(self.book.year) if self.book.year else "")
        self.genre_input = QLineEdit(self.book.genre if self.book.genre else "")

        self.layout.addWidget(QLabel("Название"))
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(QLabel("Автор"))
        self.layout.addWidget(self.author_input)
        self.layout.addWidget(QLabel("Год"))
        self.layout.addWidget(self.year_input)
        self.layout.addWidget(QLabel("Жанр"))
        self.layout.addWidget(self.genre_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_changes(self):
        self.book.title = self.title_input.text()
        self.book.author = self.author_input.text()
        self.book.year = int(self.year_input.text()) if self.year_input.text().isdigit() else None
        self.book.genre = self.genre_input.text()

        self.session.commit()
        self.accept()


# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Библиотека книг")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Год", "Жанр"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")
        self.search_button = QPushButton("Поиск")
        self.filter_button = QPushButton("Фильтрация")
        self.report_button = QPushButton("Генерация отчета")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.filter_button)
        button_layout.addWidget(self.report_button)

        self.layout.addLayout(button_layout)
        self.central_widget.setLayout(self.layout)

        self.add_button.clicked.connect(self.add_book)
        self.edit_button.clicked.connect(self.edit_book)
        self.delete_button.clicked.connect(self.delete_book)
        self.search_button.clicked.connect(self.search_book)
        self.filter_button.clicked.connect(self.filter_books)
        self.report_button.clicked.connect(self.generate_report)

        self.load_data()

    def load_data(self):
        books = session.query(Book).all()
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            self.table.setItem(row, 0, QTableWidgetItem(str(book.id)))
            self.table.setItem(row, 1, QTableWidgetItem(book.title))
            self.table.setItem(row, 2, QTableWidgetItem(book.author))
            self.table.setItem(row, 3, QTableWidgetItem(str(book.year)))
            self.table.setItem(row, 4, QTableWidgetItem(book.genre))

    def add_book(self):
        dialog = AddBookDialog(session, self)
        if dialog.exec():
            self.load_data()

    def edit_book(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для редактирования")
            return

        book_id = int(self.table.item(selected_row, 0).text())
        book = session.query(Book).get(book_id)
        dialog = EditBookDialog(session, self, book)
        if dialog.exec():
            self.load_data()

    def delete_book(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления")
            return

        book_id = int(self.table.item(selected_row, 0).text())
        book = session.query(Book).get(book_id)
        session.delete(book)
        session.commit()
        self.load_data()

    def search_book(self):
        keyword, ok = QInputDialog.getText(self, "Поиск книги", "Введите название книги:")
        if ok and keyword:
            books = session.query(Book).filter(Book.title.ilike(f"%{keyword}%")).all()
            self.table.setRowCount(len(books))
            for row, book in enumerate(books):
                self.table.setItem(row, 0, QTableWidgetItem(str(book.id)))
                self.table.setItem(row, 1, QTableWidgetItem(book.title))
                self.table.setItem(row, 2, QTableWidgetItem(book.author))
                self.table.setItem(row, 3, QTableWidgetItem(str(book.year)))
                self.table.setItem(row, 4, QTableWidgetItem(book.genre))
        else:
            QMessageBox.information(self, "Результат поиска", "Книги не найдены")

    def filter_books(self):
        genre, ok = QInputDialog.getText(self, "Фильтрация книг", "Введите жанр:")
        if ok and genre:
            books = session.query(Book).filter(Book.genre.ilike(f"%{genre}%")).all()
            self.table.setRowCount(len(books))
            for row, book in enumerate(books):
                self.table.setItem(row, 0, QTableWidgetItem(str(book.id)))
                self.table.setItem(row, 1, QTableWidgetItem(book.title))
                self.table.setItem(row, 2, QTableWidgetItem(book.author))
                self.table.setItem(row, 3, QTableWidgetItem(str(book.year)))
                self.table.setItem(row, 4, QTableWidgetItem(book.genre))
        else:
            QMessageBox.information(self, "Результат фильтрации", "Книги не найдены")

    def generate_report(self):
        books = session.query(Book).all()
        if not books:
            QMessageBox.information(self, "Отчет", "Нет данных для генерации отчета")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Отчет о книгах", ln=True, align='C')

        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        for book in books:
            pdf.cell(200, 10, txt=f"ID: {book.id}, Название: {book.title}, Автор: {book.author}, "
                                  f"Год: {book.year}, Жанр: {book.genre}", ln=True)

        report_path = "books_report.pdf"
        pdf.output(report_path)
        QMessageBox.information(self, "Отчет", f"Отчет успешно создан: {report_path}")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


# -- Создаем базу данных
# CREATE DATABASE books_db;

# -- Переходим в созданную базу данных
# USE books_db;

# -- Создаем таблицу books
# CREATE TABLE books (
#     id INT AUTO_INCREMENT PRIMARY KEY, -- Уникальный идентификатор книги
#     title VARCHAR(255) NOT NULL,       -- Название книги
#     author VARCHAR(255) NOT NULL,      -- Автор книги
#     year INT DEFAULT NULL,             -- Год выпуска книги
#     genre VARCHAR(100) DEFAULT NULL    -- Жанр книги
# );
