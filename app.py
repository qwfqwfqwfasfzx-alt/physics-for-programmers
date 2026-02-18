from flask import Flask, render_template, request, jsonify, session
import random
import math

app = Flask(__name__)
app.secret_key = 'physics_game_secret_key_2026'

# ============= БАЗА ДАННЫХ ВОПРОСОВ ДЛЯ ТЕСТА =============
QUESTIONS = [
    {
        "question": "Что гласит первый закон Ньютона (закон инерции)?",
        "options": [
            "F = m × a",
            "Тело остаётся в покое или движется равномерно прямолинейно, пока на него не подействует внешняя сила",
            "Сила действия равна силе противодействия",
            "Ускорение обратно пропорционально массе"
        ],
        "correct": 1
    },
    {
        "question": "Какая формула выражает второй закон Ньютона?",
        "options": [
            "F = m / a",
            "F = m × a",
            "F = a / m",
            "F = m + a"
        ],
        "correct": 1
    },
    {
        "question": "Что означает третий закон Ньютона для игр?",
        "options": [
            "Объекты всегда движутся с постоянной скоростью",
            "При столкновении силы равны по величине и противоположны по направлению",
            "Гравитация не влияет на объекты",
            "Масса не важна при столкновениях"
        ],
        "correct": 1
    },
    {
        "question": "Какое стандартное ускорение свободного падения (g) используется в физике Земли?",
        "options": [
            "5.67 м/с²",
            "9.81 м/с²",
            "12.34 м/с²",
            "3.14 м/с²"
        ],
        "correct": 1
    },
    {
        "question": "Какой метод оптимизации физики предлагает использовать упрощенные формы для коллайдеров?",
        "options": [
            "Использование сложных 3D-моделей",
            "Упрощенные коллайдеры (сферы, коробки)",
            "Отказ от физики",
            "Увеличение количества полигонов"
        ],
        "correct": 1
    },
    {
        "question": "Что такое LOD для физики?",
        "options": [
            "Уровень детализации для уменьшения расчетов на дальних расстояниях",
            "Тип текстуры",
            "Специальный эффект частиц",
            "Формат аудиофайлов"
        ],
        "correct": 0
    },
    {
        "question": "Какой физический движок часто используется в Unity?",
        "options": [
            "Chaos Physics",
            "PhysX",
            "Bullet",
            "Box2D"
        ],
        "correct": 1
    },
    {
        "question": "Какой физический движок предназначен специально для 2D-игр?",
        "options": [
            "Bullet Physics",
            "Chaos Physics",
            "Box2D",
            "PhysX"
        ],
        "correct": 2
    },
    {
        "question": "Что рекомендуется делать с объектами, которые не видны игроку, для оптимизации физики?",
        "options": [
            "Оставлять активными",
            "Отключать от физического расчета",
            "Увеличивать их массу",
            "Добавлять больше коллайдеров"
        ],
        "correct": 1
    },
    {
        "question": "Какая книга рекомендуется для изучения физики в играх?",
        "options": [
            "Война и мир",
            "Physics for Game Developers Дэвида Брауна",
            "1984",
            "Преступление и наказание"
        ],
        "correct": 1
    },
    {
        "question": "Что такое инерция в контексте игр?",
        "options": [
            "Объект мгновенно останавливается",
            "Объект продолжает движение после прекращения силы",
            "Объект не может двигаться",
            "Объект всегда движется по прямой"
        ],
        "correct": 1
    },
    {
        "question": "Как второй закон Ньютона применяется к прыжку персонажа?",
        "options": [
            "Сила тяжести не влияет",
            "Сила тяжести создает ускорение вниз",
            "Персонаж не может прыгать",
            "Прыжок зависит только от текстуры"
        ],
        "correct": 1
    },
    {
        "question": "Что такое отдача в оружии с точки зрения физики?",
        "options": [
            "Первый закон Ньютона",
            "Третий закон Ньютона (действие = противодействие)",
            "Второй закон Ньютона",
            "Закон сохранения энергии"
        ],
        "correct": 1
    },
    {
        "question": "Какой метод оптимизации использует многопоточность?",
        "options": [
            "Обновление физики на одном ядре",
            "Распределение нагрузки физических расчетов по ядрам процессора",
            "Отключение физики",
            "Использование только одного потока"
        ],
        "correct": 1
    },
    {
        "question": "Что такое профилирование производительности?",
        "options": [
            "Создание профиля игрока",
            "Выявление узких мест в производительности игры",
            "Настройка графики",
            "Запись видео"
        ],
        "correct": 1
    }
]

# ============= ФУНКЦИИ ДЛЯ ВЫЧИСЛЕНИЯ ПРАВИЛЬНЫХ ОТВЕТОВ =============
def calculate_jump_height(params):
    """h = v²/(2g) -> v = √(2gh)"""
    return math.sqrt(2 * params['g'] * params['target_height'])

def calculate_force(params):
    """F = m * a, a = v/t"""
    return params['m'] * params['v'] / params['t']

def calculate_acceleration(params):
    """a = (F - μ*m*g)/m"""
    return (params['F'] - params['mu'] * params['m'] * params['g']) / params['m']

def calculate_fall_velocity(params):
    """v = √(2gh)"""
    return math.sqrt(2 * params['g'] * params['h'])

def calculate_max_height(params):
    """h = (v·sin(θ))²/(2g)"""
    v_y = params['v'] * math.sin(math.radians(params['angle']))
    return (v_y ** 2) / (2 * params['g'])

def calculate_collision_velocity(params):
    """v₁' = v₁·(m₁ - m₂)/(m₁ + m₂) для упругого удара"""
    return params['v1'] * (params['m1'] - params['m2']) / (params['m1'] + params['m2'])

def calculate_spring_constant(params):
    """k = F/x"""
    return params['F'] / params['x']

def calculate_centripetal_force(params):
    """F = m·v²/R"""
    return params['m'] * params['v']**2 / params['R']

def calculate_projectile_motion(params):
    """Время полета снаряда t = 2v·sin(θ)/g"""
    return (2 * params['v'] * math.sin(math.radians(params['angle']))) / params['g']

def calculate_kinetic_energy(params):
    """E = mv²/2"""
    return (params['m'] * params['v']**2) / 2

def calculate_momentum(params):
    """p = mv"""
    return params['m'] * params['v']

def calculate_work(params):
    """A = F·s"""
    return params['F'] * params['s']

def calculate_power(params):
    """P = A/t"""
    return params['A'] / params['t']

def calculate_frequency(params):
    """f = 1/T"""
    return 1 / params['T']

# ============= ДАННЫЕ ДЛЯ ЛОКАЦИЙ =============
LOCATIONS = [
    {
        "name": "ЛАБОРАТОРИЯ КОДА",
        "background": "linear-gradient(180deg, #1a2a3a 0%, #2a3a4a 100%)",
        "ground_color": "#4a5568",
        "obstacle_color": "#ffaa66",
        "sky_objects": "code",
        "description": "Базовый уровень подготовки"
    },
    {
        "name": "ПУСТЫННЫЙ СЕРВЕР",
        "background": "linear-gradient(180deg, #d4a373 0%, #b5835a 100%)",
        "ground_color": "#c47e5a",
        "obstacle_color": "#e9c46a",
        "sky_objects": "sun",
        "description": "Жаркие пустыни"
    },
    {
        "name": "ЛЕДЯНОЙ ПРОЦЕССОР",
        "background": "linear-gradient(180deg, #a5d8ff 0%, #74c0fc 100%)",
        "ground_color": "#96f2d7",
        "obstacle_color": "#63e6be",
        "sky_objects": "snow",
        "description": "Скользкий лед"
    },
    {
        "name": "КОСМИЧЕСКАЯ СТАНЦИЯ",
        "background": "linear-gradient(180deg, #0b1020 0%, #1a1f30 100%)",
        "ground_color": "#4a5a6a",
        "obstacle_color": "#ffd966",
        "sky_objects": "planets",
        "description": "Нулевая гравитация"
    },
    {
        "name": "ДЖУНГЛИ АЛГОРИТМОВ",
        "background": "linear-gradient(180deg, #2b5e2b 0%, #1e4a1e 100%)",
        "ground_color": "#5a3e2b",
        "obstacle_color": "#ffaa66",
        "sky_objects": "leaves",
        "description": "Густая растительность"
    },
    {
        "name": "ВУЛКАНИЧЕСКИЙ ЯДЕР",
        "background": "linear-gradient(180deg, #5a1e1e 0%, #3e1a1a 100%)",
        "ground_color": "#4a2e1a",
        "obstacle_color": "#ff6b6b",
        "sky_objects": "lava",
        "description": "Раскаленная лава"
    },
    {
        "name": "КИБЕР-ГОРОД",
        "background": "linear-gradient(180deg, #1a1e3a 0%, #2a1e4a 100%)",
        "ground_color": "#4a4a6a",
        "obstacle_color": "#66ffcc",
        "sky_objects": "neon",
        "description": "Неоновые огни"
    },
    {
        "name": "ПОДВОДНЫЙ КОД",
        "background": "linear-gradient(180deg, #1e4a6a 0%, #1a3a5a 100%)",
        "ground_color": "#2e5a4a",
        "obstacle_color": "#66ccff",
        "sky_objects": "bubbles",
        "description": "Глубокий океан"
    },
    {
        "name": "ГОРНАЯ ВЕРШИНА",
        "background": "linear-gradient(180deg, #6a7a8a 0%, #4a5a6a 100%)",
        "ground_color": "#6a5a4a",
        "obstacle_color": "#ffffff",
        "sky_objects": "clouds",
        "description": "Высоко в горах"
    },
    {
        "name": "ФИНАЛЬНЫЙ БОСС",
        "background": "linear-gradient(180deg, #ffd966 0%, #ffaa66 100%)",
        "ground_color": "#b5835a",
        "obstacle_color": "#ff4d4d",
        "sky_objects": "rainbow",
        "description": "Испытание чемпионов"
    }
]

# ============= ГЕНЕРАЦИЯ ЗАДАНИЙ ПО ПРОГРАММИРОВАНИЮ =============
def generate_challenge(level=1):
    """Генерирует задачу по программированию игровой физики"""
    
    # Высота препятствия растет с уровнем
    base_height = 40 + level * 5  # высота в пикселях
    
    # Задачи по программированию игровой физики
    coding_templates = [
        {
            "name": "РЕАЛИЗАЦИЯ ПРЫЖКА",
            "description": "Допиши код для прыжка персонажа в Unity. Нужно, чтобы персонаж перепрыгнул препятствие высотой {target_height} пикс. При гравитации {g} пикс/с², какую начальную скорость (velocity) нужно задать?\n\n```csharp\npublic class PlayerController : MonoBehaviour\n{{\n    public float jumpHeight = {target_height}f;\n    public float gravity = {g}f;\n    private Rigidbody2D rb;\n\n    void Start()\n    {{\n        rb = GetComponent<Rigidbody2D>();\n    }}\n\n    void Update()\n    {{\n        if (Input.GetButtonDown(\"Jump\"))\n        {{\n            // Допиши формулу для расчета скорости прыжка\n            float jumpVelocity = Mathf.Sqrt(2 * gravity * ______);\n            rb.velocity = new Vector2(rb.velocity.x, jumpVelocity);\n        }}\n    }}\n}}\n```\n\nКакое значение нужно подставить вместо ______ ?",
            "params_template": {"g": 9.8, "target_height": base_height},
            "variable": "значение",
            "tolerance": 0.1,
            "hint": "jumpHeight - это высота прыжка. По формуле v = √(2gh)",
            "calc_func": lambda p: p['target_height'],
            "action": "jump",
            "obstacle_height": base_height + 40
        },
        {
            "name": "ФИЗИКА ДВИЖЕНИЯ",
            "description": "Реализуй движение персонажа в зависимости от массы. Вставь правильную формулу в метод FixedUpdate:\n\n```csharp\npublic class PlayerMovement : MonoBehaviour\n{{\n    public float moveForce = {F}f;\n    public float mass = {m}f;\n    private Rigidbody2D rb;\n\n    void FixedUpdate()\n    {{\n        float horizontal = Input.GetAxis(\"Horizontal\");\n        // Допиши формулу для расчета ускорения\n        float acceleration = ______ / mass;\n        rb.AddForce(Vector2.right * acceleration * moveForce);\n    }}\n}}\n```\n\nЧто должно быть в формуле ускорения? (F = m·a → a = F/m)",
            "params_template": {"F": 200, "m": 50},
            "variable": "F (сила)",
            "tolerance": 5,
            "hint": "a = F/m, где F - приложенная сила",
            "calc_func": lambda p: p['F'],
            "action": "move",
            "obstacle_height": base_height + 30
        },
        {
            "name": "ГРАВИТАЦИЯ В ИГРЕ",
            "description": "Настрой гравитацию в CustomPhysics.cs. Какое значение нужно подставить для ускорения свободного падения?\n\n```csharp\npublic class CustomPhysics : MonoBehaviour\n{{\n    public float gravity = ______; // м/с² на Земле\n    private float velocityY;\n\n    void Update()\n    {{\n        velocityY -= gravity * Time.deltaTime;\n        transform.position += Vector3.down * velocityY * Time.deltaTime;\n    }}\n}}\n```",
            "params_template": {},
            "variable": "g (м/с²)",
            "tolerance": 0.1,
            "hint": "Стандартное ускорение свободного падения на Земле - 9.8",
            "calc_func": lambda p: 9.8,
            "action": "fall",
            "obstacle_height": base_height + 20
        },
        {
            "name": "ОБРАБОТКА СТОЛКНОВЕНИЙ",
            "description": "Реализуй отскок мяча при столкновении. Какой коэффициент нужно подставить для упругого удара?\n\n```csharp\npublic class BallCollision : MonoBehaviour\n{{\n    private Rigidbody2D rb;\n\n    void OnCollisionEnter2D(Collision2D collision)\n    {{\n        // Допиши формулу для отскока\n        float bounceVelocity = -rb.velocity.y * ______;\n        rb.velocity = new Vector2(rb.velocity.x, bounceVelocity);\n    }}\n}}\n```\n\nКакой коэффициент нужен для идеально упругого удара?",
            "params_template": {},
            "variable": "коэффициент",
            "tolerance": 0.1,
            "hint": "При упругом ударе скорость меняет знак, сохраняя величину",
            "calc_func": lambda p: 1.0,
            "action": "collision",
            "obstacle_height": base_height + 40
        },
        {
            "name": "СИЛА ТРЕНИЯ",
            "description": "Реализуй силу трения в игровом движке. Какая формула расчета силы трения?\n\n```csharp\npublic class FrictionSimulation : MonoBehaviour\n{{\n    public float mass = {m}f;\n    public float frictionCoefficient = {mu}f;\n    public float gravity = {g}f;\n    private Rigidbody2D rb;\n\n    void FixedUpdate()\n    {{\n        // Допиши формулу для силы трения\n        float frictionForce = ______ * mass * gravity;\n        \n        if (rb.velocity.x > 0)\n            rb.AddForce(Vector2.left * frictionForce);\n        else if (rb.velocity.x < 0)\n            rb.AddForce(Vector2.right * frictionForce);\n    }}\n}}\n```",
            "params_template": {"mu": 0.3, "m": 50, "g": 9.8},
            "variable": "значение",
            "tolerance": 0.01,
            "hint": "Fтр = μ·m·g, где μ - коэффициент трения",
            "calc_func": lambda p: p['mu'],
            "action": "move",
            "obstacle_height": base_height + 35
        },
        {
            "name": "ИМПУЛЬС ПРИ СТОЛКНОВЕНИИ",
            "description": "Рассчитай импульс для системы частиц. Какую формулу использовать?\n\n```csharp\npublic class ParticleCollision : MonoBehaviour\n{{\n    public float mass = {m}f;\n    public float velocity = {v}f;\n\n    void OnParticleCollision()\n    {{\n        // Рассчитай импульс для эффекта взрыва\n        float momentum = ______ * velocity;\n        Debug.Log(\"Импульс: \" + momentum);\n    }}\n}}\n```",
            "params_template": {"m": 5, "v": 10},
            "variable": "значение",
            "tolerance": 0.1,
            "hint": "Импульс p = m·v",
            "calc_func": lambda p: p['m'],
            "action": "collision",
            "obstacle_height": base_height + 45
        },
        {
            "name": "КИНЕТИЧЕСКАЯ ЭНЕРГИЯ",
            "description": "Рассчитай кинетическую энергию для анимации разрушения. Вставь правильную формулу:\n\n```csharp\npublic class DestructionSystem : MonoBehaviour\n{{\n    public float mass = {m}f;\n    public float speed = {v}f;\n\n    float CalculateDestructionPower()\n    {{\n        // Верни кинетическую энергию\n        return 0.5f * ______ * speed * speed;\n    }}\n}}\n```",
            "params_template": {"m": 10, "v": 15},
            "variable": "значение",
            "tolerance": 0.1,
            "hint": "E = (m·v²)/2, где m - масса",
            "calc_func": lambda p: p['m'],
            "action": "jump",
            "obstacle_height": base_height + 40
        },
        {
            "name": "ЖЕСТКОСТЬ ПРУЖИНЫ",
            "description": "Реализуй физику пружины для платформы-батута. Какую жесткость нужно задать?\n\n```csharp\npublic class SpringPlatform : MonoBehaviour\n{{\n    public float compression = {x}f; // сжатие в метрах\n    public float force = {F}f; // приложенная сила\n\n    float GetSpringConstant()\n    {{\n        // По закону Гука F = k·x, найди k\n        return ______ / compression;\n    }}\n}}\n```",
            "params_template": {"x": 0.2, "F": 500},
            "variable": "значение",
            "tolerance": 1,
            "hint": "k = F/x, где F - сила, x - сжатие",
            "calc_func": lambda p: p['F'],
            "action": "jump",
            "obstacle_height": base_height + 50
        },
        {
            "name": "ЦЕНТРОБЕЖНАЯ СИЛА",
            "description": "Рассчитай центробежную силу для физики заноса в гоночной игре:\n\n```csharp\npublic class CarDrift : MonoBehaviour\n{{\n    public float mass = {m}f;\n    public float speed = {v}f;\n    public float turnRadius = {R}f;\n\n    float CalculateCentrifugalForce()\n    {{\n        // F = m·v²/R\n        return mass * speed * speed / ______;\n    }}\n}}\n```",
            "params_template": {"m": 5, "v": 10, "R": 3},
            "variable": "значение",
            "tolerance": 0.1,
            "hint": "В знаменателе радиус поворота",
            "calc_func": lambda p: p['R'],
            "action": "car",
            "obstacle_height": base_height + 45
        },
        {
            "name": "РАБОТА СИЛЫ",
            "description": "Рассчитай работу силы для подъема платформы:\n\n```csharp\npublic class PlatformLift : MonoBehaviour\n{{\n    public float force = {F}f;\n    public float distance = {s}f;\n\n    float CalculateWork()\n    {{\n        // Работа A = F·s\n        return ______ * distance;\n    }}\n}}\n```",
            "params_template": {"F": 100, "s": 5},
            "variable": "значение",
            "tolerance": 1,
            "hint": "A = F·s, где F - сила, s - расстояние",
            "calc_func": lambda p: p['F'],
            "action": "move",
            "obstacle_height": base_height + 30
        }
    ]
    
    # Выбираем шаблон с учетом уровня
    template = coding_templates[(level - 1) % len(coding_templates)].copy()
    
    # Генерируем параметры
    params = {}
    for key, value in template['params_template'].items():
        if key == 'g':
            params[key] = 9.8
        elif key == 'target_height':
            params[key] = base_height
        elif key == 'm':
            params[key] = random.randint(10, 100)
        elif key == 'v':
            params[key] = random.randint(5, 20)
        elif key == 'F':
            params[key] = random.randint(50, 500)
        elif key == 'mu':
            params[key] = round(random.uniform(0.1, 0.5), 1)
        elif key == 'x':
            params[key] = round(random.uniform(0.1, 0.5), 1)
        elif key == 'R':
            params[key] = random.randint(2, 8)
        elif key == 's':
            params[key] = random.randint(2, 10)
        elif key == 't':
            params[key] = random.randint(1, 5)
        elif key == 'A':
            params[key] = random.randint(100, 1000)
        elif key == 'T':
            params[key] = round(random.uniform(0.5, 2.0), 1)
        else:
            params[key] = value
    
    # Получаем локацию для этого уровня
    location = LOCATIONS[(level - 1) % len(LOCATIONS)]
    
    # Форматируем описание с параметрами
    description = template["description"].format(**params)
    
    # Создаем финальный словарь задания
    challenge = {
        "name": template["name"],
        "description": description,
        "params": params,
        "variable": template["variable"],
        "tolerance": template["tolerance"],
        "hint": template["hint"],
        "level": level,
        "action": template.get("action", "jump"),
        "obstacle_height": template["obstacle_height"],
        "location": location
    }
    
    # Вычисляем правильное значение
    correct_value = template["calc_func"](params)
    challenge["correct_value"] = correct_value
    
    return challenge

# ============= МАРШРУТЫ =============
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/theory')
def theory():
    return render_template('theory.html')

@app.route('/materials')
def materials():
    return render_template('materials.html')

@app.route('/learning')
def learning():
    return render_template('learning.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        data = request.get_json()
        question_index = data.get('question_index')
        selected = data.get('selected')
        
        q_list = session.get('question_list', [])
        if question_index < len(q_list):
            q = q_list[question_index]
            correct = q['correct']
            if selected == correct:
                session['score'] = session.get('score', 0) + 1
                return jsonify({'correct': True, 'score': session['score']})
            else:
                return jsonify({'correct': False, 'score': session['score']})
        return jsonify({'error': 'Question index out of range'}), 400
    
    session['question_list'] = random.sample(QUESTIONS, min(15, len(QUESTIONS)))
    session['score'] = 0
    return render_template('test.html', questions=session['question_list'])

@app.route('/game')
def game():
    # Инициализируем игру
    session['game_score'] = 0
    session['game_level'] = 1
    session['best_score'] = session.get('best_score', 0)
    session['games_played'] = session.get('games_played', 0) + 1
    
    # Генерируем первое задание
    challenge = generate_challenge(1)
    session['current_challenge'] = challenge
    
    return render_template('game.html', 
                         challenge=challenge, 
                         best_score=session['best_score'],
                         games_played=session['games_played'])

@app.route('/check_game', methods=['POST'])
def check_game():
    data = request.get_json()
    user_value = float(data.get('value'))
    challenge = session.get('current_challenge')
    
    if not challenge:
        return jsonify({'error': 'No active challenge'}), 400
    
    correct = challenge['correct_value']
    tolerance = challenge['tolerance']
    
    if abs(user_value - correct) <= tolerance:
        # Правильно
        current_level = session.get('game_level', 1)
        points = 5 * current_level
        
        session['game_score'] = session.get('game_score', 0) + points
        session['game_level'] = current_level + 1
        
        if session['game_score'] > session.get('best_score', 0):
            session['best_score'] = session['game_score']
        
        # Если достигнут 10 уровень, начинаем заново с бонусом
        if session['game_level'] > 10:
            session['game_score'] += 50  # бонус за прохождение
            session['game_level'] = 1
        
        new_challenge = generate_challenge(session['game_level'])
        session['current_challenge'] = new_challenge
        
        return jsonify({
            'success': True,
            'new_challenge': new_challenge,
            'score': session['game_score'],
            'best_score': session['best_score'],
            'level': session['game_level'],
            'points_earned': points
        })
    else:
        game_score = session.get('game_score', 0)
        best_score = session.get('best_score', 0)
        
        session['game_score'] = 0
        session['game_level'] = 1
        
        return jsonify({
            'success': False,
            'score': game_score,
            'best_score': best_score,
            'correct_answer': round(correct, 2),
            'level': challenge['level']
        })

if __name__ == '__main__':
    app.run(debug=True)