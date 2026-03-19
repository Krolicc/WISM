## Бэкенд

Бэкенд — это приложение на Python, созданное с помощью FastAPI.

### Ключевые директории и файлы:

*   `backend/app`: Содержит основную логику приложения.
*   `backend/app/api`: Определения конечных точек API.
*   `backend/app/crud`: Функции для операций создания, чтения, обновления и удаления в базе данных.
*   `backend/app/models`: Модели базы данных (SQLAlchemy).
*   `backend/app/schemas`: Схемы Pydantic для валидации данных.
*   `backend/app/services`: Сервисы с бизнес-логикой.
*   `backend/main.py`: Точка входа для приложения FastAPI.

### Модели данных (app/models)
*   **`Story`**: Основная сущность, представляющая историю. Содержит `title`, `description` и т.д.
*   **`Chapter`**: Глава внутри истории.
    *   `id`: UUID
    *   `title`: String
    *   `description`: Text
    *   `order`: Integer, **Порядковый номер главы в истории.**
    *   `story_id`: ForeignKey(Story)
    *   `created_at`: DateTime
    *   `updated_at`: DateTime
*   **`Scene`**: Сцена внутри главы.
    *   `id`: UUID
    *   `title`: String
    *   `description`: Text
    *   `order`: Integer, **Порядковый номер сцены в главе.**
    *   `chapter_id`: ForeignKey(Chapter)
    *   `created_at`: DateTime
    *   `updated_at`: DateTime
*   **`Frame`**: Кадр (панель) внутри сцены.
    *   `id`: UUID
    *   `order`: Integer, **Порядковый номер кадра в сцене.**
    *   `common_description`: Text
    *   `detailed_prompt`: JSONB
    *   `image_url`: String
    *   `scene_id`: ForeignKey(Scene)
    *   `created_at`: DateTime
    *   `updated_at`: DateTime
