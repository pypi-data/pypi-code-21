from .utils import map_model

__all__ = ["QueryObject"]


class QueryObject:
    """Core JsonQL Query Object Class

    Attributes:
        model_class (SQLAlchemy): SQLAlchemy Model Class
        session (SQLAlchemy): SQLAlchemy session
        fields (dict): Mapped fields. If it is None, it will be auto-generated based on model_class at init
    """

    model_class = None
    session = None
    fields = None

    def __init__(self, **kwargs):
        if self.model_class is None:
            if kwargs.get("model_class"):
                self.model_class = kwargs['model_class']
            else:
                raise ValueError("model_class not defined")
        if self.session is None:
            if kwargs.get("session"):
                self.session = kwargs['session']
            else:
                raise ValueError("session not defined")
        if self.fields is None:
            self.fields = map_model(self.model_class)

    def create(self, data):
        """Create Method

        Create new record.

        Args:
            data (dict): Query Body

        Returns:
            int: idx field of new record if model has idx field else None
        """

        new_object = self.model_class()
        for field, field_dict in self.fields.items():
            if not field_dict["auto_increment"]:
                field_value = data.get(field)
                if field_value is not None:
                    setattr(new_object, field,
                            field_dict['type'].format_input(field_value))
                elif field_dict["nullable"] or field_dict["default"]:
                    pass
                else:
                    raise KeyError(field + " didn't passed.")
        self.session.add(new_object)
        self.session.commit()
        return new_object.idx if hasattr(self.model_class, "idx") else None

    def read(self, data):
        """Read Method

        Reads records that match a given query condition

        Args:
            data (dict): Query Body

        Returns:
            dict or list: if model has idx key query result will return by dict type, else list type
        """

        has_idx_key = hasattr(self.model_class, "idx")

        query_object = self.model_class.query
        for filter_key, filter_value in data.items():
            if filter_key in self.fields.keys():
                query_object = query_object.filter_by(**{
                    filter_key: self.fields[filter_key]['type'].format_input(
                        filter_value)})
        if has_idx_key:
            query_object = query_object.order_by(self.model_class.idx.desc())
        query_object = query_object.all()

        result_data = {} if has_idx_key else []
        if query_object:
            for result_item in query_object:
                kookql_json = {}
                for field, field_dict in self.fields.items():
                    kookql_json[field] = field_dict['type'].format_output(
                        getattr(result_item, field))
                if has_idx_key:
                    result_data[int(getattr(result_item, "idx"))] = kookql_json
                else:
                    result_data.append(kookql_json)

        return result_data

    def update(self, data):
        """Update Method

        Update record of a given primary key in query

        Args:
            data (dict): Query Body

        Returns:
            bool: query result
        """

        query_object = self.model_class.query.get(data["id"])
        del data["id"]
        if query_object:
            for update_key, update_value in data.items():
                if update_key in self.fields.keys():
                    setattr(query_object, update_key,
                            self.fields[update_key]['type'].format_input(update_value))
            self.session.add(query_object)
            self.session.commit()
            return True
        else:
            return False

    def delete(self, data):
        """Delete Method

        Delete record of a given primary key in query

        Args:
            data (dict): Query Body

        Returns:
            bool: query result
        """

        query_object = self.model_class.query.get(data["id"])
        if query_object:
            self.session.delete(query_object)
            self.session.commit()
            return True
        else:
            return False
