
from sqlalchemy.orm import Session
from typing import Any, List, Dict
from app.crud.crud_entity import crud_entity, CRUDEntity
from app.schemas.entity import EntityUpdate

class CRDTManager:
    def __init__(self, crud: CRUDEntity):
        self.crud = crud

    def patch(
        self, 
        db: Session, 
        *, 
        entity_id: str, 
        path: List[str], 
        old_value: Any, 
        new_value: Any
    ) -> bool:
        """
        Atomically updates a nested field within a JSON 'data' column of an entity.
        
        :param db: The database session.
        :param entity_id: The ID of the entity to update.
        :param path: A list of keys to traverse to the target field.
        :param old_value: The expected current value of the field (for conflict detection).
        :param new_value: The new value to set for the field.
        :return: True if the update was successful, False if a conflict occurred or the path is invalid.
        """
        db_obj = self.crud.get(db=db, id=entity_id)
        if not db_obj or not db_obj.data:
            return False

        # Work with a copy of the data to avoid side effects
        data_copy = dict(db_obj.data)
        current_level = data_copy

        # Traverse the path to the parent of the target field
        try:
            for key in path[:-1]:
                current_level = current_level[key]
        except (KeyError, TypeError):
            # Invalid path
            return False

        leaf_key = path[-1]
        
        # Get the current value and perform the compare-and-swap
        current_value = current_level.get(leaf_key)

        if current_value == old_value:
            # If values match, update the field
            current_level[leaf_key] = new_value
            
            # Use the existing CRUD update mechanism
            update_schema = EntityUpdate(data=data_copy)
            self.crud.update(db=db, db_obj=db_obj, obj_in=update_schema)
            
            return True
        else:
            # Conflict detected, the data has been changed by another process
            return False

# Singleton instance of the manager
crdt_manager = CRDTManager(crud_entity)
