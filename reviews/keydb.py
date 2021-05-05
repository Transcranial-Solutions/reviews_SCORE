from iconservice import DictDB, VarDB, IconScoreDatabase

class KeyDB:
    """
    Database abstraction to store keys. It is not ordered.
    """

    _NAME = '_KeyDB'


    def __init__(self, var_key: str, db: IconScoreDatabase, value_type: type):
        self._name = var_key + KeyDB._NAME
        self._index_to_key = DictDB(f'{self._name}_index_to_key', db, value_type = type)
        self._key_to_index = DictDB(f'{self._name}_key_to_index', db, value_type = int)
        self._key_count = VarDB(f'{self._name}_key_count', db, value_type = int)

    def __contains__(self, key) -> bool:
        if self._key_to_index[key]:
            return True
        else:
            return False
    
    def __iter__(self):
        for index in range(1, self._key_count.get() + 1):
            yield self._index_to_key[index]
    
    def add_key(self, key) -> None:
        """
        Add a key.
        """
        next_index = self._key_count.get() + 1
        self._index_to_key[next_index] = key
        self._key_to_index[key]
        self._key_count.set(next_index)


    def remove_key(self, key) -> None:
        """
        Remove a key.
        """
        # Get information needed for key removal.
        current_index = self._key_to_index[key]
        last_index = self._key_count.get()
        key_at_last_index = self._index_to_key[last_index]
        _key_count = last_index

        # Different removal procedure depending on conditions.
        if _key_count == 1 or current_index == last_index:  
            self._delete_key(key)
        
        else:
            self._delete_key(key)
            self._assign_key_new_index(key_at_last_index, current_index)

        # Decrement key counter.
        self._key_count.set(_key_count - 1)

    def _assign_key_new_index(self, key, new_index: int) -> None:
        """
        Assign a key to a new index. 
        """
        # Remove old index.
        old_index = self._key_to_index[key]
        del self._index_to_key[old_index]
        del self._key_to_index[key]

        # Assign new index.
        self._key_to_index[key] = new_index
        self._index_to_key[new_index] = key
    
    def _delete_key(self, key) -> None:
        """
        Delete a key. 
        """
        index = self._key_to_index[key]
        del self._index_to_key[index]
        del self._key_to_index[key]
