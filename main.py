from abc import ABC, abstractmethod
import pickle
import os

class Book:
    def __init__(self, title, author, status="Доступна"):
        self.__title = title
        self.__author = author
        self.__status = status
       
    @property
    def title(self):
        return self.__title
    
    @property
    def author(self):
        return self.__author
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, value):
        if value in ["Доступна", "Выдана"]:
            self.__status = value
        else:
            raise ValueError("Неверный статус книги")

class User(ABC):
    def __init__(self, name):
        self.__name = name
                
    @property
    def name(self):
        return self.__name

    @abstractmethod
    def get_role(self):
        pass

class Reader(User):
    def __init__(self, name):
        super().__init__(name)  
        self.borrowed_books = []
    
    def get_role(self):  
        return "Читатель"

    def user_system(self, library, user_manager):
        while True:
            username = input("Как вас зовут? ").strip()
                
            if not username:
                print("Имя не может быть пустым!")
                continue
            
            current_user = user_manager.find_user_by_name(username)
            
            if not current_user:
                print(f"Добро пожаловать, {username}!")
                current_user = Reader(username)
                user_manager.users.append(current_user)
                library.save_data()
            else:
                print(f"С возвращением, {username}!")
                print(f"У вас взято книг: {len(current_user.borrowed_books)}")
            
            while True:
                print("\n1. Просмотреть доступные книги")
                print("2. Взять книгу")
                print("3. Вернуть книгу")
                print("4. Просмотреть список взятых моих книг")
                print("0. Выход")
                
                choice = int(input("Выберите действие: "))

                if choice == 1:
                    self.show_available_books(library)
                elif choice == 2:
                    self.borrow_book(library, current_user, user_manager)
                elif choice == 3:
                    self.return_book(current_user, library, user_manager)
                elif choice == 4:
                    self.view_my_books(current_user, library)
                elif choice == 0:
                    print(f"\nДо свидания, {current_user.name}!")
                    break
                else:
                    print("Неверный выбор!")
                
    def show_available_books(self, library):
        available_books = [book for book in library.books 
                          if book.status == "Доступна"]
        
        if not available_books:
            print("К сожалению, все книги сейчас выданы")
            return
        
        print(f"Найдено {len(available_books)} доступных книг:")
        
        for i, book in enumerate(available_books, 1):
            print(f"{i}. {book.title} - {book.author}")
            
    def borrow_book(self, library, current_user, user_manager):
        available_books = [book for book in library.books 
                          if book.status == "Доступна"]
        
        if not available_books:
            print("Нет доступных книг для взятия")
            return
        
        print("Доступные книги:")
        for i, book in enumerate(available_books, 1):
            print(f"{i}. {book.title} - {book.author}")
        
        try:
            book_num = int(input("\nВведите номер книги для взятия (0 - отмена): "))
            
            if book_num == 0:
                print("Отмена")
                return
            
            if book_num < 1 or book_num > len(available_books):
                print("Неверный номер книги!")
                return
            
            selected_book = available_books[book_num - 1]
            
            if selected_book in current_user.borrowed_books:
                print(f"Вы уже взяли книгу '{selected_book.title}'!")
                return

            selected_book.status = "Выдана"
            current_user.borrowed_books.append(selected_book)
            library.save_data()
            
            print(f"\nВы успешно взяли книгу:")
            print(f"Название книги: '{selected_book.title}'")
            print(f"Автор: {selected_book.author}")
            
        except ValueError:
            print("Введите число!")
            
    def return_book(self, current_user, library, user_manager):
        if not current_user.borrowed_books:
            print("У вас нет взятых книг")
            return
        
        print("Ваши взятые книги:")
        for i, book in enumerate(current_user.borrowed_books, 1):
            print(f"{i}. {book.title} - {book.author}")
        
        try:
            book_num = int(input("\nВведите номер книги для возврата (0 - отмена): "))
            
            if book_num == 0:
                print("Отмена")
                return
            
            if book_num < 1 or book_num > len(current_user.borrowed_books):
                print("Неверный номер книги!")
                return

            returned_book = current_user.borrowed_books.pop(book_num - 1)
            returned_book.status = "Доступна"
            library.save_data()
            
            print(f"\nВы вернули книгу:")
            print(f"'{returned_book.title}'")
            
        except ValueError:
            print("Введите число!")
        
    def view_my_books(self, current_user, library):
        print(f"\n{current_user.name}: Мои книги")
        
        if not current_user.borrowed_books:
            print("У вас нет взятых книг")
        else:
            print(f"Всего книг: {len(current_user.borrowed_books)}")
            
            for i, book in enumerate(current_user.borrowed_books, 1):
                print(f"{i}. {book.title}")
                print(f"Автор: {book.author}")

class Library:
    def __init__(self):
        self.books = []
        self.load_data()
        
    def save_data(self):
        try:
            data = {
                'books': self.books,
                'users': UserManager.users
            }
            with open('library_data.pkl', 'wb') as f:
                pickle.dump(data, f)
            print("Все данные успешно сохранены")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            return False
    
    def load_data(self):
        try:
            if os.path.exists('library_data.pkl'):
                with open('library_data.pkl', 'rb') as f:
                    data = pickle.load(f)
                    self.books = data.get('books', [])
                    UserManager.users = data.get('users', [])
                print(f"Загружено {len(self.books)} книг и {len(UserManager.users)} пользователей")
                return True
            else:
                print("Файл с данными не существует...")
                return False
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
            return False
    
    def show_books(self):
        if not self.books:
            print("В библиотеке нет добавленных книг")
            return False
        
        print("\nСписок всех книг:")
        for i, book in enumerate(self.books, 1):
            status_text = "Доступна" if book.status == "Доступна" else "Выдана"
            print(f"{i}. {book.title}/{book.author}/{status_text}")
        
        return True

class UserManager:
    users = []
    
    def __init__(self):
        pass
    
    def register_user(self, library):
        username = input("Введите ваш юз: ")
        
        if not username:
            print("Имя не может быть пустым")
            return False
        
        for user in self.users:
            if user.name.lower() == username.lower():
                print("Пользователь уже существует")
                return False
            
        new_user = Reader(username)
        self.users.append(new_user)
        library.save_data()
        print("Пользователь успешно зарегистрирован!")
        return True
    
    @classmethod
    def find_user_by_name(cls, username):
        for user in cls.users:
            if user.name.lower() == username.lower():
                return user
        return None
    
    @classmethod
    def show_all_users(cls):
        if not cls.users:
            print("Нет зарегистрированных пользователей")
            return
        
        print("\nСписок всех пользователей:")
        for i, user in enumerate(cls.users, 1):
            books_count = len(user.borrowed_books)
            print(f"{i}. {user.name} - книг взято: {books_count}")

class Librarian(User):
    def __init__(self, name=""):
        super().__init__(name)
      
    def get_role(self):
        return "Библиотекарь" 
     
    def system(self, library, user_manager):
        name_input = input("Как вас зовут? ")
        
        if name_input:
            self._User__name = name_input
        
        while True:
            print("\nЗдравствуйте,", self.name)
            print("\nЧто вы хотите сделать?")
            print("1. Добавление книги")
            print("2. Удаление книги")
            print("3. Зарегистрировать нового пользователя")
            print("4. Просмотреть список всех пользователей")
            print("5. Просмотреть список всех книг (с их статусами)")
            print("0. Выход")
            choice = int(input("\nВыберите пожалуйста действие: "))
            
            if choice == 1:
                self.add_book(library)
            elif choice == 2:
                self.remove_book(library)
            elif choice == 3:
                user_manager.register_user(library)
            elif choice == 4:
                user_manager.show_all_users()
            elif choice == 5:
                library.show_books()
            elif choice == 0:
                break
            
    def add_book(self, library):
        title = input("Название книги: ")
        author = input("Автор книги: ")
        
        for book in library.books:
            if book.title == title and book.author == author:
                print("Извините! Такая книга уже существует")
                return
        new_book = Book(title, author, "Доступна")
        
        library.books.append(new_book)
        library.save_data()
        
        print(f"Книга {title} успешно добавлена!")
        
    def remove_book(self, library):
        if not library.show_books():
            print("Нет книг для удаления")
            return
        
        try:
            book_num = int(input("Введите номер книги, которую хотите удалить (для выхода нажмите 0): "))
            
            if book_num == 0:
                print("Отмена")
                return
            
            if book_num < 1 or book_num > len(library.books):
                print("Неверный номер книги")
                return
            
            book_to_remove = library.books[book_num - 1]
            
            print(f"Выбрана: {book_to_remove.title} - {book_to_remove.author} со статусом {book_to_remove.status}")
            
            if book_to_remove.status == "Выдана":
                print("Книга выдана читателю, как только он вернет, тогда можно и удалить :)")
                return
            
            removed_book = library.books.pop(book_num - 1)
            library.save_data()

            print(f"Библиотекарь: {self.name} удалил книгу: {removed_book.title}")

        except Exception as e:
            print(f"Ошибка: {e}")

class Console:
    def run(self):
        library = Library()
        user_manager = UserManager()

        print("Добро пожаловать в библиотеку!")
        while True:
            print("Кто ты воин?")
            print("1. Библиотекарь")
            print("2. Читатель")
            print("3. Выход")
            
            choose = int(input("\nВыберите один из пунктов: "))
            match(choose):
                case 1:
                    librarian = Librarian(name="")
                    librarian.system(library, user_manager)
                case 2:
                    reader = Reader("")
                    reader.user_system(library, user_manager)
                case 3:
                    library.save_data()
                    print("До свидания!")
                    break
                case _:
                    print("Неверный выбор")

console = Console()
console.run()