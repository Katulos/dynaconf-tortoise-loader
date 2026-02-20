# Examples of using dynaconf with Tortoise ORM

This directory contains examples of using dynaconf with Tortoise ORM.

## Usage

1. Install the package using `pip`:

   ```bash
   pip install -e .
   ```

2. Run app:

   ```bash
   python -m app
   ```

3. Check db using `sqlite` (optional):

   ```bash
   echo "SELECT * FROM dynaconf_storage;" | sqlite3 data/settings.sqlite3
   ```

   The command output should be similar to:

   ```
   1|MYAPP_MAIN|_INITIALIZED|@bool True
   2|MYAPP_MAIN|MY_CUSTOM_SETTING|test_value_123
   3|MYAPP_MAIN|ANOTHER_SETTING|@int 42
   4|MYAPP_MAIN|NESTED_CONFIG|@json {"key1": "value1", "key2": [1, 2, 3]}
   5|MYAPP_MAIN|APP_UPTIME|@int 3600
   6|MYAPP_MAIN|APP_STATUS|running
   7|MYAPP_MAIN|APP_USERS_COUNT|@int 150
   ```
