Хорошо. Давай начнем с самого начала. У нас уже интегрирован neo4j Начнем с адаптации уровней с PDB в neo4j. Анализируем "backend/app/models"

---

Отлично. Начинаем "Блок 2: Определение Новой 'Анатомии' Повествования". Мы проанализируем текущие модели SQLAlchemy в backend/app/models и решим, что "уезжает" в Neo4j, а что остается в PostgreSQL.

Это самый важный этап проектирования. От него зависит чистота и эффективность всей будущей системы.

Начинаю анализ. Сначала мне нужно получить список всех моделей, чтобы ничего не упустить.

Анализ backend/app/models завершен.

Story: id, title, description. Хранит arcs (связь One-to-Many).
Arc: id, title, overview, story_id, order. Хранит chapters (O2M).
Chapter: id, title, overview, arc_id, order. Хранит scenes (O2M).
Scene: id, title, overview, chapter_id, order. Хранит frames и entities_in_scene (O2M).
Frame: id, title, overview, scene_id, order.
Entity / EntityInScene: Это наша старая, "плоская" модель, которую мы уже решили переделать.
Теперь мы проведем "хирургическую операцию". Мы разделим каждую модель на две части: "графовую" (структура и связи) и "реляционную" (контент).

Neo4j становится нашим единым источником правды для структуры повествования.

Узлы (Nodes):

(:Story {id, title})
(:Arc {id, title})
(:Chapter {id, title})
(:Scene {id, title})
(:Frame {id, title})
(:Entity {id, name, type}) - Наша новая каноническая картотека сущностей.
Связи (Relationships):

Иерархия: (:Story)-[:CONTAINS]->(:Arc)-[:CONTAINS]->(:Chapter)-...
Последовательность: (:Arc)-[:NEXT]->(:Arc), (:Chapter)-[:NEXT]->(:Chapter), и т.д.
Значимость: (:Entity)-[:RELEVANT_TO]->(:Arc), (:Entity)-[:RELEVANT_TO]->(:Chapter)
Появление: (:Entity)-[:APPEARS_IN]->(:Scene)
Важнейшее изменение: Поля order и все внешние ключи (story_id, arc_id и т.д.) из старой модели полностью исчезают. Их заменяют связи в Neo4j.

PostgreSQL становится нашим "складом" для "тяжелого" контента. Модели значительно упрощаются.

stories_content:

story_id (Primary Key, совпадает с ID узла в Neo4j)
description (TEXT)
...другие "тяжелые" поля, например, URL обложки
arcs_content:

arc_id (PK)
overview (TEXT)
chapters_content:

chapter_id (PK)
overview (TEXT)
scenes_content:

scene_id (PK)
overview (TEXT)
full_text (TEXT, опционально)
frames_content:

frame_id (PK)
overview (TEXT)
entities_content:

entity_id (PK)
description (TEXT) - Каноническое описание персонажа.
portrait_url (VARCHAR, опционально)
Создать новые модели SQLAlchemy: Мы должны создать новые файлы моделей, отражающие эту "контентную" структуру (stories_content, arcs_content и т.д.).
Удалить старые связи и поля: Избавиться от relationship(), ForeignKey, и полей order в существующих моделях.
Создать GraphService: Начать реализацию GraphService, который будет содержать Cypher-запросы для создания узлов и связей на основе новой модели.
Адаптировать API: Переписать, например, эндпоинт POST /stories/{story_id}/arcs, чтобы он:
Создавал узел (:Arc) в Neo4j.
Создавал связь [:CONTAINS] от (:Story) к новому (:Arc).
Создавал запись в таблице arcs_content в PostgreSQL.
(Опционально) Устанавливал связь [:NEXT] с предыдущей аркой.
Это радикальное, но чистое и правильное разделение. Мы готовы приступить к реализации. Начнем с создания новых моделей?