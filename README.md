<h1 align="center">
  🛒 AI EcomDRF &nbsp;—&nbsp; Scalable Django Backend for E-Commerce with LLM, Payments & Celery
</h1>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/Ilya88556/AI-Ecom-DRF/ci.yml?label=CI&logo=github" />
  <img src="https://img.shields.io/badge/Coverage-96%25-brightgreen" />
  <img src="https://img.shields.io/badge/Python-3.12-blue" />
  <img src="https://img.shields.io/badge/Deploy-Local--Docker-blue" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

<details>
<summary>English</summary>

# 🚀 Key Features

This project implements a full-fledged **backend architecture for an e-commerce platform** with advanced modular structure, AI product description generation, payment simulation, and background tasks. It's designed as a strong base for scalable online stores.

- 📂 **Modular Architecture**. Each domain (Store, Cart, Orders, Payments, Delivery, Users) lives in a separate Django app. This separation supports clean code, easier maintenance, and migration to microservices if needed.
- 🔐 **Secure Authentication**. Djoser / JWT endpoints allow any frontend or mobile app to connect easily with standardized logic.
- ⚡ **Fast Catalog**. Tree-like categories (MPTT), optimized queries (`select_related`, `prefetch_related`), pagination. Provides a quick UX, reducing bounce and cart abandonment rates.
- 🛒 **Reliable Cart**. All actions (`add / update / remove`) wrapped in `transaction.atomic()`. Only one active cart per user avoids accidental reorders or duplicates.
- 💳 **One-click Checkout** — `Cart → Order + Delivery` created in one transaction. Simple, robust flow for frontend developers and integrations. (Emulation)
- 🏦 **Multi-gateway Payments**. Mock SDKs for LiqPay, Fondy, Monobank with signature verification and callback support. Business instantly knows payment status. (Emulated)
- 📦 **Nova Poshta Integration**. Ukrainian national delivery service integration. Celery tasks keep delivery data (areas, cities, warehouses) synced. Up-to-date delivery points reduce return rates.
- 🤖 **AI Product Assistant**. One-click generation of persuasive product descriptions from price, brand, features. Saves content managers hours and increases product page conversion.

# 🛠️ Technologies

🧩 Full library stack:

- ## ⚙️ Backend / ORM / API
  - **Python 3.12**
  - **Django 5.1 LTS** + **Django REST Framework 3.15**
  - **drf-spectacular** — Auto Swagger / OpenAPI 3
  - **PostgreSQL** (`psycopg2-binary`)
  - **Django MPTT** — Tree categories
  - **django-filter** — Advanced filtering
  - **Grappelli** + `django-object-actions` — Extended admin
  - **django-ckeditor-5** — WYSIWYG admin fields
  - **Django Debug Toolbar** — Profiling in dev

- ## 🔐 Authentication / Social Login
  - **Djoser** endpoints
  - **Simple JWT** access / refresh

- ## ⚡ Async / Background
  - **Celery 5.5 + Redis 5**
  - **django-celery-beat** — Cron-like tasks in admin

- ## 🏦 Payments / Delivery
  - Mock SDKs: **LiqPay, Fondy, Monobank**
  - **Requests / httpx** for external APIs
  - **Nova Poshta** REST v2 API

- ## 🤖 AI & LLM
  - **OpenAI Python SDK v1** — Generates marketing descriptions

- ## 🧪 Testing & Quality
  - **Pytest 8**, **pytest-django**, **pytest-cov** (96 % coverage)
  - **Factory Boy**, **Faker**
  - **Black**, **isort**, **flake8**
  - **coverage.py + htmlcov** — full HTML report

- ## 📦 DevOps
  - **Docker + docker-compose v3.9**
  - **GitHub Actions**
  - **environs**

# 🏗️ Architecture

This is a **modular monolith**: one Django project where each business domain lives in a dedicated Django app. Combines ease of deployment with clear boundaries, and allows gradual replacement with services if needed.

- ## 📐 App Layers

  - **API** — DRF ViewSets, serializers, validation, filters
  - **Services / Application Layer** — Business logic, transactions (`transaction.atomic()`), payment & delivery factories
  - **Domain (ORM)** — Pure Django models. Source of truth.
  - **API Tests** — Business logic tested via HTTP using `APIClient`
  - **Transactions** — Atomic control over data integrity

- ## 🗄️ Data Storage

  - **PostgreSQL** — Primary data store
  - Indexed hot fields (`is_active`, `ordering`, FK) for performance
  - `select_related` / `prefetch_related` eliminate N+1 queries
  - DB-level constraints (Unique / Check) protect from invalid data

- ## ⚙️ Async Tasks & Integration

  - **Celery + Redis** — Sync Nova Poshta locations on schedule
  - **PaymentFactory** — Integrate LiqPay / Fondy / Monobank through a single interface
  - **DeliveryFactory** — Easily add new carriers (Nova Poshta, Pickup)
  - **Gateway Exceptions** — External API errors don’t crash the app

- ## 🔍 Observability & Developer Experience

  - **Docker-first** — Consistent local and CI setup
  - **GitHub Actions** — Linting, tests, and coverage per pull request

# ⚙️ Setup / Run (Linux)

This section contains the **Docker-based setup instructions**.

- ## 📝 Requirements

  - **Git**
  - **Docker Engine** ≥ 24
  - **Docker Compose Plugin**

- ## 🚀 Clone the repository

  ~~~bash
  git clone https://github.com/Ilya88556/AI-Ecom-DRF.git
  cd AI-Ecom-DRF
  ~~~

- ## 🔑 Setup environment variables

  - Set `NOVA_POSHTA_API_KEY` — [Nova Poshta API](https://developers.novaposhta.ua/documentation)
  - Set `OPEN_API_KEY` — [OpenAI SDK](https://github.com/openai/openai-python)
  - Set email server config

- ## 🏗️ Build and run containers

  ~~~bash
  docker compose up --build
  ~~~

- ## 🗄️ Create Django superuser

  ~~~bash
  docker compose exec backend python manage.py createsuperuser
  ~~~

- ## 🌐 Open the app

  - <http://localhost:8000/admin/> — **Admin (Grappelli)**
  - <http://localhost:8000/api/v1/docs/swagger/> — **Swagger / OpenAPI**
  - <http://localhost:8000/api/v1/docs/redoc/> — **Redoc**

- ## 🛑 Stop & remove containers

  ~~~bash
  docker compose down
  ~~~

# 📡 API

- All endpoints are RESTful, versioned under `/api/v1/`
- **OpenAPI 3** auto-generated docs available:
  - Swagger UI — http://localhost:8000/api/v1/docs/swagger/
  - ReDoc — http://localhost:8000/api/v1/docs/redoc/

# 🧪 Testing

**Coverage** | **≈ 96 %** |
- Tests run automatically via **GitHub Actions** on push & PR.

- ## Tools
  - **pytest + pytest-django** — test suite
  - **coverage.py** — coverage measurement
  - **unittest.mock (MagicMock / patch)** — mocking
  - **factory_boy** — model factories
  - **faker** — fake data generators
  - Rich set of **custom fixtures** for API, models, etc.

<details>
<summary>📊 <strong>Coverage Report (96 %)</strong> &nbsp;—&nbsp; click to expand</summary>

```text
Name                                         Stmts   Miss  Cover  
----------------------------------------------------------------  
cart\__init__.py                                 0      0   100%  
cart\admin.py                                   24      3    88%  
cart\apps.py                                     4      0   100%  
cart\cart_service.py                            38      5    87%  
cart\migrations\0001_initial.py                  5      0   100%  
cart\migrations\0002_initial.py                  7      0   100%  
cart\migrations\__init__.py                      0      0   100%  
cart\models.py                                  45      3    93%  
cart\serializers.py                             39      1    97%  
cart\tests\__init__.py                           0      0   100%  
cart\tests\conftest.py                          25      0   100%  
cart\tests\test_cart_views.py                  210      3    99%  
cart\urls.py                                     5      0   100%  
cart\views.py                                   67      6    91%  
delivery\__init__.py                             0      0   100%  
delivery\admin.py                               32      2    94%  
delivery\apps.py                                 4      0   100%  
delivery\factory.py                             13      2    85%  
delivery\gateways\__init__.py                    0      0   100%  
delivery\gateways\base.py                       12      2    83%  
delivery\gateways\novaposhta.py                 44     28    36%  
delivery\gateways\pickup.py                     10      0   100%  
delivery\management\__init__.py                  0      0   100%  
delivery\migrations\0001_initial.py              8      0   100%  
delivery\migrations\0002_initial.py              6      0   100%  
delivery\migrations\__init__.py                  0      0   100%  
delivery\models.py                              63      4    94%  
delivery\serializers.py                         23      0   100%  
delivery\services.py                            16      0   100%  
delivery\tests\__init__.py                       0      0   100%  
delivery\tests\conftest.py                      32      0   100%  
delivery\tests\test_services.py                106      0   100%  
delivery\tests\test_view.py                    208      0   100%  
delivery\urls.py                                 5      0   100%  
delivery\views.py                               28      0   100%  
ecom_drf_v1\__init__.py                          2      0   100%  
ecom_drf_v1\celery.py                            6      0   100%  
ecom_drf_v1\settings.py                         56      0   100%  
ecom_drf_v1\urls.py                              9      0   100%  
orders\__init__.py                               0      0   100%  
orders\admin.py                                 25      3    88%  
orders\apps.py                                   4      0   100%  
orders\migrations\0001_initial.py                5      0   100%  
orders\migrations\0002_initial.py                7      0   100%  
orders\migrations\__init__.py                    0      0   100%  
orders\models.py                                30      1    97%  
orders\serializers.py                           27      0   100%  
orders\services.py                              37      2    95%  
orders\tests\__init__.py                         0      0   100%  
orders\tests\conftest.py                        25      0   100%  
orders\tests\test_order_view.py                217      0   100%  
orders\urls.py                                   5      0   100%  
orders\views.py                                 35      1    97%  
payments\__init__.py                             0      0   100%  
payments\admin.py                                8      0   100%  
payments\apps.py                                 4      0   100%  
payments\exceptions.py                           6      0   100%  
payments\factory.py                              9      0   100%  
payments\gateways\__init__.py                    0      0   100%  
payments\gateways\base.py                       10      2    80%  
payments\gateways\fondy.py                      26     12    54%  
payments\gateways\liqpay.py                     26      0   100%  
payments\gateways\monobank.py                   26     12    54%  
payments\migrations\0001_initial.py              6      0   100%  
payments\migrations\__init__.py                  0      0   100%  
payments\models.py                              18      1    94%  
payments\permissions.py                          9      0   100%  
payments\serializers.py                          7      0   100%  
payments\services.py                            46      6    87%  
payments\tests\__init__.py                       0      0   100%  
payments\tests\conftest.py                      22      0   100%  
payments\tests\test_views.py                   170      1    99%  
payments\urls.py                                 5      0   100%  
payments\utils.py                                9      0   100%  
payments\views.py                               49      1    98%  
store\__init__.py                                0      0   100%  
store\admin.py                                 100     11    89%  
store\apps.py                                    4      0   100%  
store\filters.py                                19      0   100%  
store\migrations\0001_initial.py                 9      0   100%  
store\migrations\0002_initial.py                 7      0   100%  
store\migrations\__init__.py                     0      0   100%  
store\mixins.py                                 17      2    88%  
store\models.py                                189     13    93%  
store\permissions.py                            21      2    90%  
store\serializers.py                           137      0   100%  
store\tests\__init__.py                          0      0   100%  
store\tests\conftest.py                        125      1    99%  
store\tests\test_product_ai_description.py      46      0   100%  
store\tests\test_serializers.py                 39      0   100%  
store\tests\test_utils.py                       24      0   100%  
store\tests\test_views.py                     1240     35    97%  
store\urls.py                                   11      0   100%  
store\utils.py                                  31      0   100%  
store\views.py                                 109      6    94%  
users\__init__.py                                0      0   100%  
users\admin.py                                   8      0   100%  
users\apps.py                                    4      0   100%  
users\migrations\0001_initial.py                 6      0   100%  
users\migrations\__init__.py                     0      0   100%  
users\models.py                                 41      9    78%  
users\serializers.py                            32      8    75%  
users\tests\__init__.py                          0      0   100%  
users\tests\conftest.py                         35      4    89%  
users\tests\test_validators.py                  21      0   100%  
users\tests\test_views.py                       74      0   100%  
users\urls.py                                    2      0   100%  
users\validators.py                             11      0   100%  
----------------------------------------------------------------  
TOTAL                                         4387    192    96%
```
</details>

# 📄 License  
This project is licensed under the [MIT License](LICENSE).

</details>
<details>
<summary>Українською</summary>

# 🚀 Ключові особливості

Цей проєкт реалізує backend-архітектуру для інтернет-магазину з розширеною структурою, AI, оплатами та фоновими задачами. Підходить як основа для масштабованих e-commerce рішень.

- 📂 **Модульна архітектура.** Кожен домен (Store, Cart, Orders, Payments, Delivery, Users) реалізований у власному Django-додатку. Це зручно для масштабування та переходу до мікросервісів.
- 🔐 **Безпечна автентифікація.** Стандартизовані Djoser/JWT endpoint-и. Підключення будь-якого фронту або мобільного застосунку без складної логіки.
- ⚡ **Швидкий каталог.** Ієрархічні категорії (MPTT), оптимізовані запити (select/prefetch_related), пагінація. Швидкий відгук сторінки зменшує відмови та покинуті кошики.
- 🛒 **Надійний кошик.** Усі дії (add / update / remove) обгорнуті в transaction.atomic(), у кожного користувача завжди лише один активний кошик. Це виключає випадкові повторні покупки.
- 💳 **Оформлення замовлення в один клік.** Cart → Order + Delivery створюються транзакційно. Надійна логіка для фронту та інтеграцій.
- 🏦 **Оплата через кілька шлюзів (LiqPay, Fondy, Monobank) з перевіркою підписів і callback.** Зручно клієнту, миттєве оновлення статусу. (Емуляція)
- 📦 **Інтеграція з «Новою Поштою».** Celery-задачі синхронізують області, міста, відділення. Актуальні дані — менше повернень.
- 🤖 **AI-асистент.** Один клік в адмінці генерує "продаючий" опис товару з урахуванням ціни, бренду, категорії. Економить години рутини контент менеджеру, та збільшує конверсію продуктових карток.

# 🛠️ Технології

🧩 Повний стек бібліотек.

- ## ⚙️ Backend / ORM / API
  - **Python 3.12**
  - **Django 5.1 LTS** + **Django REST Framework 3.15**
  - **drf-spectacular** — Swagger / OpenAPI 3
  - **PostgreSQL**
  - **Django MPTT** — ієрархічні категорії
  - **django-filter** — фільтри
  - **Grappelli** + `django-object-actions` - розширена адмін панель
  - **django-ckeditor-5** — WYSIWYG у адмін панелі
  - **Django Debug Toolbar** - профілювання запитів

- ## 🔐 Автентифікація / соц-логін
  - **Djoser**
  - **Simple JWT** access / refresh

- ## ⚡ Async / Фон
  - **Celery 5.5 + Redis 5**
  - **django-celery-beat** - Завдання за розкладом у панелі адміністратора

- ## 🏦 Оплати / Доставка
  - SDK-моки: **LiqPay, Fondy, Monobank**
  - **Requests / httpx**
  - **Нова Пошта** REST v2 API

- ## 🤖 AI & LLM
  - **OpenAI Python SDK v1** - Генерування маркетингового опису товарів

- ## 🧪 Тестування
  - **Pytest 8**, **pytest-django**, **pytest-cov** (96 % coverage)
  - **Factory Boy**, **Faker**
  - **Black**, **isort**, **flake8**
  - **coverage.py + htmlcov**

- ## 📦 DevOps
  - **Docker + docker-compose v3.9**
  - **GitHub Actions**
  - **environs**

# 🏗️ Архітектура

Проєкт — **модульний моноліт**: усі домени в окремих Django-app. Проста підтримка, чіткі межі відповідальності, можливість переходу до мікросервісів.

- ## 📐 Рівні застосунку

  - **API** — DRF ViewSets, Serializers, фільтрація
  - **Services / Application** — логіка, транзакції, фабрики
  - **Domain (ORM)** — моделі без сигналів
  - **API-тести** — Тестування бизнес логіки через HTTP p допомогою APIClient
  - **Транзакції** — контроль цілісності

- ## 🗄️ Зберігання даних

  - **PostgreSQL**
  - Індекси на «гарячих» полях (`is_active`, `ordering`, FK)
  - `select_related` / `prefetch_related` - Оптимізування запитів для уникнення N+1 проблеми
  - DB‑обмеження (Unique, Check) — для захисту від помилок

- ## ⚙️ Фон і інтеграції

  - **Celery + Redis** - Синхронізація активних відділень "Нова Пошта" за розкладом
  - PaymentFactory — єдина точка доступу для платіжних шлюзів  
  - DeliveryFactory — NovaPoshta, Pickup, нові carrier‑и  
  - `GatewayException` — контроль помилок зовнішньго API

- ## 🔍 Спостереження та зручність розробки

  - **Docker-first**
  - **GitHub Actions**

# ⚙️ Встановлення / Запуск (Linux)

- ## 📝 Попередні вимоги

  - **Git**
  - **Docker Engine** ≥ 24
  - **Docker Compose Plugin**

- ## 🚀 Клонування репозиторію

  ~~~bash
  git clone 
  cd llm-shop-drf-backend
  ~~~

- ## 🔑 Змінні оточення

  - `NOVA_POSHTA_API_KEY` — [Nova Poshta API](https://developers.novaposhta.ua/documentation)
  - `OPEN_API_KEY` — [OpenAI SDK](https://github.com/openai/openai-python)
  - Налаштування пошти

- ## 🏗️ Збірка і запуск

  ~~~bash
  docker compose up --build
  ~~~

- ## 🗄️ Створити суперкористувача

  ~~~bash
  docker compose exec backend python manage.py createsuperuser
  ~~~

- ## 🌐 Перегляд

  - http://localhost:8000/admin/ — адмінка  
  - http://localhost:8000/api/v1/docs/swagger/ — Swagger  
  - http://localhost:8000/api/v1/docs/redoc/ — ReDoc

- ## 🛑 Зупинка

  ~~~bash
  docker compose down
  ~~~

# 📡 API

- Всі endpoint-и у форматі REST, версія `/api/v1/`
- Специфікація **OpenAPI 3**:
  - Swagger: http://localhost:8000/api/v1/docs/swagger/
  - ReDoc: http://localhost:8000/api/v1/docs/redoc/

# 🧪 Тести

**Покриття** | **≈ 96 %**
- CI запускає тести в GitHub Actions

- ## Інструменти  
  - **pytest + pytest-django**  
  - **coverage.py**  
  - **unittest.mock (MagicMock / patch)**  
  - **factory_boy**  
  - **faker**  
  - **кастомні фікстури**

<details>
<summary>📊 <strong>Coverage Report (96 %)</strong> &nbsp;—&nbsp; натисни, щоб розгорнути</summary>

```text
Name                                         Stmts   Miss  Cover  
----------------------------------------------------------------  
cart\__init__.py                                 0      0   100%  
cart\admin.py                                   24      3    88%  
cart\apps.py                                     4      0   100%  
cart\cart_service.py                            38      5    87%  
cart\migrations\0001_initial.py                  5      0   100%  
cart\migrations\0002_initial.py                  7      0   100%  
cart\migrations\__init__.py                      0      0   100%  
cart\models.py                                  45      3    93%  
cart\serializers.py                             39      1    97%  
cart\tests\__init__.py                           0      0   100%  
cart\tests\conftest.py                          25      0   100%  
cart\tests\test_cart_views.py                  210      3    99%  
cart\urls.py                                     5      0   100%  
cart\views.py                                   67      6    91%  
delivery\__init__.py                             0      0   100%  
delivery\admin.py                               32      2    94%  
delivery\apps.py                                 4      0   100%  
delivery\factory.py                             13      2    85%  
delivery\gateways\__init__.py                    0      0   100%  
delivery\gateways\base.py                       12      2    83%  
delivery\gateways\novaposhta.py                 44     28    36%  
delivery\gateways\pickup.py                     10      0   100%  
delivery\management\__init__.py                  0      0   100%  
delivery\migrations\0001_initial.py              8      0   100%  
delivery\migrations\0002_initial.py              6      0   100%  
delivery\migrations\__init__.py                  0      0   100%  
delivery\models.py                              63      4    94%  
delivery\serializers.py                         23      0   100%  
delivery\services.py                            16      0   100%  
delivery\tests\__init__.py                       0      0   100%  
delivery\tests\conftest.py                      32      0   100%  
delivery\tests\test_services.py                106      0   100%  
delivery\tests\test_view.py                    208      0   100%  
delivery\urls.py                                 5      0   100%  
delivery\views.py                               28      0   100%  
ecom_drf_v1\__init__.py                          2      0   100%  
ecom_drf_v1\celery.py                            6      0   100%  
ecom_drf_v1\settings.py                         56      0   100%  
ecom_drf_v1\urls.py                              9      0   100%  
orders\__init__.py                               0      0   100%  
orders\admin.py                                 25      3    88%  
orders\apps.py                                   4      0   100%  
orders\migrations\0001_initial.py                5      0   100%  
orders\migrations\0002_initial.py                7      0   100%  
orders\migrations\__init__.py                    0      0   100%  
orders\models.py                                30      1    97%  
orders\serializers.py                           27      0   100%  
orders\services.py                              37      2    95%  
orders\tests\__init__.py                         0      0   100%  
orders\tests\conftest.py                        25      0   100%  
orders\tests\test_order_view.py                217      0   100%  
orders\urls.py                                   5      0   100%  
orders\views.py                                 35      1    97%  
payments\__init__.py                             0      0   100%  
payments\admin.py                                8      0   100%  
payments\apps.py                                 4      0   100%  
payments\exceptions.py                           6      0   100%  
payments\factory.py                              9      0   100%  
payments\gateways\__init__.py                    0      0   100%  
payments\gateways\base.py                       10      2    80%  
payments\gateways\fondy.py                      26     12    54%  
payments\gateways\liqpay.py                     26      0   100%  
payments\gateways\monobank.py                   26     12    54%  
payments\migrations\0001_initial.py              6      0   100%  
payments\migrations\__init__.py                  0      0   100%  
payments\models.py                              18      1    94%  
payments\permissions.py                          9      0   100%  
payments\serializers.py                          7      0   100%  
payments\services.py                            46      6    87%  
payments\tests\__init__.py                       0      0   100%  
payments\tests\conftest.py                      22      0   100%  
payments\tests\test_views.py                   170      1    99%  
payments\urls.py                                 5      0   100%  
payments\utils.py                                9      0   100%  
payments\views.py                               49      1    98%  
store\__init__.py                                0      0   100%  
store\admin.py                                 100     11    89%  
store\apps.py                                    4      0   100%  
store\filters.py                                19      0   100%  
store\migrations\0001_initial.py                 9      0   100%  
store\migrations\0002_initial.py                 7      0   100%  
store\migrations\__init__.py                     0      0   100%  
store\mixins.py                                 17      2    88%  
store\models.py                                189     13    93%  
store\permissions.py                            21      2    90%  
store\serializers.py                           137      0   100%  
store\tests\__init__.py                          0      0   100%  
store\tests\conftest.py                        125      1    99%  
store\tests\test_product_ai_description.py      46      0   100%  
store\tests\test_serializers.py                 39      0   100%  
store\tests\test_utils.py                       24      0   100%  
store\tests\test_views.py                     1240     35    97%  
store\urls.py                                   11      0   100%  
store\utils.py                                  31      0   100%  
store\views.py                                 109      6    94%  
users\__init__.py                                0      0   100%  
users\admin.py                                   8      0   100%  
users\apps.py                                    4      0   100%  
users\migrations\0001_initial.py                 6      0   100%  
users\migrations\__init__.py                     0      0   100%  
users\models.py                                 41      9    78%  
users\serializers.py                            32      8    75%  
users\tests\__init__.py                          0      0   100%  
users\tests\conftest.py                         35      4    89%  
users\tests\test_validators.py                  21      0   100%  
users\tests\test_views.py                       74      0   100%  
users\urls.py                                    2      0   100%  
users\validators.py                             11      0   100%  
----------------------------------------------------------------  
TOTAL                                         4387    192    96%
```
</details>

# 📄 **Ліцензія**  
Проєкт ліцензовано під [MIT License](LICENSE).
</details>
