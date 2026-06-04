import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Achievement
from quiz.models import Category, Quiz, Question, Answer
from django.contrib.auth import get_user_model

User = get_user_model()

# Create achievements
achievements_data = [
    {'name': 'Первый шаг', 'description': 'Пройди первую викторину', 'icon': '🌱', 'category': 'quiz', 'points_reward': 50, 'requirement_value': 1},
    {'name': 'Десятка', 'description': 'Пройди 10 викторин', 'icon': '🔟', 'category': 'quiz', 'points_reward': 100, 'requirement_value': 10},
    {'name': 'Ветеран', 'description': 'Пройди 50 викторин', 'icon': '🎖️', 'category': 'quiz', 'points_reward': 250, 'requirement_value': 50},
    {'name': 'Новичок в серии', 'description': 'Играй 3 дня подряд', 'icon': '🔥', 'category': 'streak', 'points_reward': 75, 'requirement_value': 3},
    {'name': 'Неделя', 'description': 'Играй 7 дней подряд', 'icon': '📅', 'category': 'streak', 'points_reward': 150, 'requirement_value': 7},
    {'name': 'Первые очки', 'description': 'Набери 100 очков', 'icon': '⭐', 'category': 'score', 'points_reward': 50, 'requirement_value': 100},
    {'name': 'Богатый игрок', 'description': 'Набери 1000 очков', 'icon': '💰', 'category': 'score', 'points_reward': 200, 'requirement_value': 1000},
    {'name': 'Снайпер', 'description': 'Достигни точности 80%', 'icon': '🎯', 'category': 'accuracy', 'points_reward': 100, 'requirement_value': 80},
]

for a in achievements_data:
    Achievement.objects.get_or_create(name=a['name'], defaults=a)

print(f"✅ Создано {Achievement.objects.count()} достижений")

# Create categories
categories_data = [
    {'name': 'Наука', 'icon': '🔬', 'color': '#6366f1', 'description': 'Физика, химия, биология'},
    {'name': 'История', 'icon': '📜', 'color': '#f59e0b', 'description': 'Мировая история'},
    {'name': 'География', 'icon': '🌍', 'color': '#22c55e', 'description': 'Страны, столицы, природа'},
    {'name': 'Технологии', 'icon': '💻', 'color': '#3b82f6', 'description': 'IT и технологии'},
    {'name': 'Культура', 'icon': '🎭', 'color': '#ec4899', 'description': 'Искусство, кино, музыка'},
    {'name': 'Спорт', 'icon': '⚽', 'color': '#ef4444', 'description': 'Спорт и рекорды'},
]

cats = {}
for c in categories_data:
    cat, _ = Category.objects.get_or_create(name=c['name'], defaults=c)
    cats[c['name']] = cat

print(f"✅ Создано {Category.objects.count()} категорий")

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@quiz.com', 'admin123')
    print("✅ Создан суперпользователь admin / admin123")

# Create demo user
if not User.objects.filter(username='demo').exists():
    User.objects.create_user('demo', 'demo@quiz.com', 'demo123')
    print("✅ Создан демо-пользователь demo / demo123")

# Create sample quizzes
def create_quiz(title, desc, category_name, difficulty, time_limit, questions_data):
    cat = cats.get(category_name)
    if not cat:
        return
    admin = User.objects.get(username='admin')
    quiz, created = Quiz.objects.get_or_create(
        title=title,
        defaults={'description': desc, 'category': cat, 'difficulty': difficulty,
                  'time_limit': time_limit, 'created_by': admin}
    )
    if created:
        for i, qd in enumerate(questions_data):
            q = Question.objects.create(
                quiz=quiz, text=qd['q'], order=i, points=10, explanation=qd.get('exp', '')
            )
            for ai, a in enumerate(qd['answers']):
                Answer.objects.create(question=q, text=a['text'], is_correct=a.get('correct', False))
    return quiz

create_quiz(
    'Основы Python', 'Проверь знания Python', 'Технологии', 'easy', 30,
    [
        {'q': 'Как вывести текст в Python?', 'exp': 'Функция print() выводит текст на экран',
         'answers': [{'text': 'print("Hello")', 'correct': True}, {'text': 'echo "Hello"'}, {'text': 'console.log("Hello")'}, {'text': 'printf("Hello")'}]},
        {'q': 'Какой тип данных у значения True?', 'exp': 'True и False — объекты типа bool',
         'answers': [{'text': 'bool', 'correct': True}, {'text': 'int'}, {'text': 'str'}, {'text': 'NoneType'}]},
        {'q': 'Как создать список в Python?', 'exp': 'Квадратные скобки создают список (list)',
         'answers': [{'text': '[1, 2, 3]', 'correct': True}, {'text': '{1, 2, 3}'}, {'text': '(1, 2, 3)'}, {'text': 'list{1, 2, 3}'}]},
        {'q': 'Что делает функция len()?', 'exp': 'len() возвращает количество элементов',
         'answers': [{'text': 'Возвращает длину объекта', 'correct': True}, {'text': 'Удаляет объект'}, {'text': 'Копирует объект'}, {'text': 'Сортирует объект'}]},
        {'q': 'Как начать комментарий в Python?', 'exp': 'Символ # начинает однострочный комментарий',
         'answers': [{'text': '#', 'correct': True}, {'text': '//'}, {'text': '/*'}, {'text': '--'}]},
    ]
)

create_quiz(
    'Великие открытия', 'История научных открытий', 'Наука', 'medium', 25,
    [
        {'q': 'Кто открыл теорию относительности?', 'exp': 'Альберт Эйнштейн опубликовал специальную теорию относительности в 1905 году',
         'answers': [{'text': 'Альберт Эйнштейн', 'correct': True}, {'text': 'Исаак Ньютон'}, {'text': 'Никола Тесла'}, {'text': 'Стивен Хокинг'}]},
        {'q': 'Что такое ДНК?', 'exp': 'ДНК — дезоксирибонуклеиновая кислота, носитель генетической информации',
         'answers': [{'text': 'Носитель генетической информации', 'correct': True}, {'text': 'Вид белка'}, {'text': 'Тип жирной кислоты'}, {'text': 'Химический элемент'}]},
        {'q': 'Сколько планет в Солнечной системе?', 'exp': 'После 2006 года Плутон был переклассифицирован, осталось 8 планет',
         'answers': [{'text': '8', 'correct': True}, {'text': '9'}, {'text': '7'}, {'text': '10'}]},
        {'q': 'Из чего состоит вода?', 'exp': 'Молекула воды H₂O состоит из 2 атомов водорода и 1 атома кислорода',
         'answers': [{'text': 'Водород и кислород', 'correct': True}, {'text': 'Водород и азот'}, {'text': 'Кислород и углерод'}, {'text': 'Только водород'}]},
        {'q': 'Что изучает астрономия?', 'exp': 'Астрономия — наука о небесных телах, их движении и строении',
         'answers': [{'text': 'Небесные тела и космос', 'correct': True}, {'text': 'Атомы и молекулы'}, {'text': 'Живые организмы'}, {'text': 'Строение Земли'}]},
    ]
)

create_quiz(
    'Столицы мира', 'Знаешь столицы разных стран?', 'География', 'easy', 20,
    [
        {'q': 'Столица Франции?', 'answers': [{'text': 'Париж', 'correct': True}, {'text': 'Лион'}, {'text': 'Марсель'}, {'text': 'Бордо'}]},
        {'q': 'Столица Японии?', 'answers': [{'text': 'Токио', 'correct': True}, {'text': 'Осака'}, {'text': 'Киото'}, {'text': 'Нагасаки'}]},
        {'q': 'Столица Бразилии?', 'exp': 'Бразилиа стала столицей в 1960 году, сменив Рио-де-Жанейро',
         'answers': [{'text': 'Бразилиа', 'correct': True}, {'text': 'Рио-де-Жанейро'}, {'text': 'Сан-Паулу'}, {'text': 'Манаус'}]},
        {'q': 'Столица Австралии?', 'exp': 'Канберра — специально построенная столица Австралии',
         'answers': [{'text': 'Канберра', 'correct': True}, {'text': 'Сидней'}, {'text': 'Мельбурн'}, {'text': 'Брисбен'}]},
        {'q': 'Столица Канады?', 'exp': 'Оттава — столица Канады, а не Торонто (крупнейший город)',
         'answers': [{'text': 'Оттава', 'correct': True}, {'text': 'Торонто'}, {'text': 'Монреаль'}, {'text': 'Ванкувер'}]},
    ]
)

print(f"✅ Создано {Quiz.objects.count()} викторин с {Question.objects.count()} вопросами")
print("\n🎉 База данных успешно заполнена демо-данными!")
print("   Логин: admin / admin123")
print("   Логин: demo / demo123")
