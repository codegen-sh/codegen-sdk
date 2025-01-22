# unittest to pytest Migration Example

[![Documentation](https://img.shields.io/badge/docs-docs.codegen.com-blue)](https://docs.codegen.com/tutorials/unittest-to-pytest)

This example demonstrates how to use Codegen to automatically migrate unittest test suites to pytest. For a complete walkthrough, check out our [tutorial](https://docs.codegen.com/tutorials/unittest-to-pytest).

## What This Example Does

The migration script handles four key transformations:

1. **Convert Test Classes and Setup Methods**
   ```python
   # From:
   class TestUsers(unittest.TestCase):
       def setUp(self):
           self.db = setup_test_db()

       def test_create_user(self):
           user = self.db.create_user("test")
           self.assertEqual(user.name, "test")

   # To:
   @pytest.fixture
   def db():
       db = setup_test_db()
       yield db

   def test_create_user(db):
       user = db.create_user("test")
       assert user.name == "test"
   ```

2. **Update Assertions**
   ```python
   # From:
   def test_validation(self):
       self.assertTrue(is_valid("test"))
       self.assertEqual(count_items(), 0)
       self.assertRaises(ValueError, parse_id, "invalid")

   # To:
   def test_validation():
       assert is_valid("test")
       assert count_items() == 0
       with pytest.raises(ValueError):
           parse_id("invalid")
   ```

3. **Convert Test Discovery**
   ```python
   # From:
   if __name__ == '__main__':
       unittest.main()

   # To:
   # Remove unittest.main() and rename files to test_*.py
   ```

4. **Modernize Fixtures**
   ```python
   # From:
   @classmethod
   def setUpClass(cls):
       cls.conn = create_db()

   # To:
   @pytest.fixture(scope="session")
   def conn():
       return create_db()
   ```

## Running the Example

```bash
# Install Codegen
pip install codegen

# Run the migration
python run.py
```

The script will process all Python test files in the `repo-before` directory and apply the transformations in the correct order.

## Understanding the Code

- `run.py` - The migration script
- `repo-before/` - Sample unittest test suite to migrate
- `guide.md` - Additional notes and explanations

## Learn More

- [Full Tutorial](https://docs.codegen.com/tutorials/unittest-to-pytest)
- [pytest Documentation](https://docs.pytest.org/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Codegen Documentation](https://docs.codegen.com)