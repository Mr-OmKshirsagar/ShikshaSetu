import pytest
from app.igot.prototype_adapter import PrototypeIGOTAdapter


class MockCollection:
    def __init__(self):
        self.last_query = None

    def find(self, query):
        self.last_query = query
        class MockCursor:
            def sort(self, *args): return self
            def skip(self, *args): return self
            def limit(self, *args): return []
            def __iter__(self): return iter([])
        return MockCursor()

    def count_documents(self, query):
        self.last_query = query
        return 0


class MockDatabase:
    def __init__(self):
        self.learning_resources = MockCollection()


def test_igot_search_escapes_regex_metacharacters():
    db = MockDatabase()
    adapter = PrototypeIGOTAdapter(db)

    # Searching with dangerous metacharacters
    malicious_input = "[unclosed_bracket(and_paren*+?^$"
    adapter.list_courses(search_query=malicious_input)

    regex_pattern = db.learning_resources.last_query["title"]["$regex"]
    # Verify that literal brackets were escaped
    assert "\\[" in regex_pattern
    assert "\\(" in regex_pattern
    assert "\\*" in regex_pattern
    assert "\\+" in regex_pattern
    assert "\\?" in regex_pattern
    assert "\\^" in regex_pattern
    assert "\\$" in regex_pattern
