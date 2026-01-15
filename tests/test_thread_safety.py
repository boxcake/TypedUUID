"""Tests for TypedUUID thread safety."""
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest

from typed_uuid import TypedUUID, create_typed_uuid_class


class TestThreadSafety:
    """Tests for thread-safe operations on TypedUUID."""

    def test_concurrent_class_creation_same_type(self):
        """Test creating the same TypedUUID class from multiple threads."""
        results = []
        errors = []

        def create_class():
            try:
                cls = create_typed_uuid_class('Thread', 'thread')
                results.append(cls)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_class) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # All results should be the same class
        assert len(results) == 100
        assert all(r is results[0] for r in results)

    def test_concurrent_class_creation_different_types(self):
        """Test creating different TypedUUID classes from multiple threads."""
        results = {}
        errors = []
        lock = threading.Lock()

        def create_class(type_id):
            try:
                cls = create_typed_uuid_class(f'Type{type_id}', type_id)
                with lock:
                    results[type_id] = cls
            except Exception as e:
                with lock:
                    errors.append(e)

        type_ids = [f't{i}' for i in range(50)]  # t0, t1, ..., t49
        threads = [threading.Thread(target=create_class, args=(tid,)) for tid in type_ids]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # All types should be registered
        assert len(results) == 50
        for tid in type_ids:
            assert TypedUUID.is_type_registered(tid)

    def test_concurrent_instance_creation(self):
        """Test creating TypedUUID instances from multiple threads."""
        UserUUID = create_typed_uuid_class('User', 'usr')
        results = []
        errors = []
        lock = threading.Lock()

        def create_instance():
            try:
                instance = UserUUID()
                with lock:
                    results.append(instance)
            except Exception as e:
                with lock:
                    errors.append(e)

        threads = [threading.Thread(target=create_instance) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # All instances should be valid and unique
        assert len(results) == 100
        unique_uuids = set(str(r) for r in results)
        assert len(unique_uuids) == 100

    def test_concurrent_registry_access(self):
        """Test accessing registry from multiple threads while creating classes."""
        errors = []
        lock = threading.Lock()

        # Pre-create some classes
        for i in range(10):
            create_typed_uuid_class(f'Pre{i}', f'pre{i}')

        def read_registry():
            try:
                for _ in range(100):
                    TypedUUID.list_registered_types()
                    TypedUUID.is_type_registered('pre0')
                    TypedUUID.get_class_by_type_id('pre1')
            except Exception as e:
                with lock:
                    errors.append(e)

        def create_classes():
            try:
                for i in range(10):
                    create_typed_uuid_class(f'New{i}', f'new{i}')
            except Exception as e:
                with lock:
                    errors.append(e)

        # Start reader and writer threads concurrently
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=read_registry))
            threads.append(threading.Thread(target=create_classes))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

    def test_thread_pool_executor(self):
        """Test using ThreadPoolExecutor for concurrent operations."""

        def create_and_use(type_id):
            cls = create_typed_uuid_class(f'Pool{type_id}', type_id)
            instance = cls()
            return str(instance)

        type_ids = [f'p{i}' for i in range(20)]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_and_use, tid) for tid in type_ids]
            results = [f.result() for f in as_completed(futures)]

        # All operations should complete successfully
        assert len(results) == 20

        # All results should be valid typed UUIDs
        for result in results:
            assert '-' in result
            parts = result.split('-', 1)
            assert len(parts) == 2

    def test_concurrent_validation(self):
        """Test validating UUIDs from multiple threads."""
        UserUUID = create_typed_uuid_class('User', 'vld')
        test_uuid = 'vld-550e8400-e29b-41d4-a716-446655440000'
        results = []
        errors = []
        lock = threading.Lock()

        def validate():
            try:
                instance = UserUUID.from_string(test_uuid)
                with lock:
                    results.append(instance)
            except Exception as e:
                with lock:
                    errors.append(e)

        threads = [threading.Thread(target=validate) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # All results should be valid
        assert len(results) == 100
        for r in results:
            assert str(r) == test_uuid
