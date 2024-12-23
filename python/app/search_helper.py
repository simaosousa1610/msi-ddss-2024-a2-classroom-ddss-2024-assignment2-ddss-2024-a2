from sqlalchemy import or_
from models import Book

class SearchLogic:
    @staticmethod
    def _escape_input(string):
        return string.replace('%', r'\%').replace('_', r'\_')

    @staticmethod
    def search_phrase(query, search_field, search_input):
        if not search_input:
            return query
        
        search_input = SearchLogic._escape_input(search_input)
        return query.filter(getattr(Book, search_field).ilike(f'%{search_input}%'), escape='\\')

    @staticmethod
    def search_all(query, search_field, search_input):
        if not search_input:
            return query

        if not hasattr(Book, search_field):
            return query
        
        search_input = SearchLogic._escape_input(search_input)

        for word in search_input.split():
            query = query.filter(getattr(Book, search_field).ilike(f'%{word}%'))
        
        return query

    @staticmethod
    def search_any(query, search_field, search_input):
        if not search_input:
            return query
        
        search_input = SearchLogic._escape_input(search_input)

        conditions = [getattr(Book, search_field).ilike(f'%{word}%') for word in search_input.split()]
        return query.filter(or_(*conditions))

    @staticmethod
    def search_any_field_phrase(query, search_input):
        if not search_input:
            return query
        
        search_input = SearchLogic._escape_input(search_input)

        fields = [Book.title, Book.authors, Book.category, Book.description, Book.keywords, Book.notes]
        conditions = [field.ilike(f'%{search_input}%') for field in fields]
        return query.filter(or_(*conditions))

    @staticmethod
    def search_any_field_all(query, search_input):
        if not search_input:
            return query
        
        search_input = SearchLogic._escape_input(search_input)

        words = search_input.strip().split()
        fields = [Book.title, Book.authors, Book.category, Book.description, Book.keywords, Book.notes]
        
        combined_filter = query
        for word in words:
            word_filter = or_(*[field.ilike(f'%{word}%') for field in fields])
            combined_filter = combined_filter.filter(word_filter)
        
        return combined_filter

    @staticmethod
    def search_any_field_any(query, search_input):

        if not search_input:
            return query
        
        search_input = SearchLogic._escape_input(search_input)

        words = search_input.strip().split()
        fields = [Book.title, Book.authors, Book.category, Book.description, Book.keywords, Book.notes]
        conditions = [field.ilike(f'%{word}%') for word in words for field in fields]
        return query.filter(or_(*conditions))

    @staticmethod
    def v_search_phrase(query, search_field, search_input):
        if not search_input:
            return query
        
        return query.filter(getattr(Book, search_field).ilike(f'%{search_input}%'), escape='\\')

    @staticmethod
    def v_search_all(query, search_field, search_input):
        if not search_input:
            return query

        if not hasattr(Book, search_field):
            return query
        
        for word in search_input.split():
            query = query.filter(getattr(Book, search_field).ilike(f'%{word}%'))
        
        return query

    @staticmethod
    def v_search_any(query, search_field, search_input):
        if not search_input:
            return query
        
        conditions = [getattr(Book, search_field).ilike(f'%{word}%') for word in search_input.split()]
        return query.filter(or_(*conditions))

    @staticmethod
    def v_search_any_field_phrase(query, search_input):
        if not search_input:
            return query
        
        fields = [Book.title, Book.authors, Book.category, Book.description, Book.keywords, Book.notes]
        conditions = [field.ilike(f'%{search_input}%') for field in fields]
        return query.filter(or_(*conditions))

    @staticmethod
    def v_search_any_field_all(query, search_input):
        if not search_input:
            return query
        
        words = search_input.strip().split()
        fields = [Book.title, Book.authors, Book.category, Book.description, Book.keywords, Book.notes]
        
        combined_filter = query
        for word in words:
            word_filter = or_(*[field.ilike(f'%{word}%') for field in fields])
            combined_filter = combined_filter.filter(word_filter)
        
        return combined_filter

    @staticmethod
    def v_search_any_field_any(query, search_input):

        if not search_input:
            return query
        
        words = search_input.strip().split()
        fields = [Book.title, Book.authors, Book.category, Book.description, Book.keywords, Book.notes]
        conditions = [field.ilike(f'%{word}%') for word in words for field in fields]
        return query.filter(or_(*conditions))