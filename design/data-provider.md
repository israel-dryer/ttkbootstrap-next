# Data Provider

The data provider class is a mixin that enables robust handling of data provided to a widget. This provider will provide
loading, callbacks, crud operations, sorting, and paging functionality.

## Model

The data provided works with a list of dictionaries.

Each record should have an "id" field at a minimum. An "key_field" and "value_field" can be provided to lookup these
items from the provided dictionary data source.

## Crud Operations

This class provides a mechanism for creating, updating, deleting, and reading data.


## DataSource

**Options**
- sort
- filter
- select

**Events**
- changed
- load error
- loading changed

## Data Store
- load
- insert
- remove
- update
- by_key
- total_count

## Stores
- in_memory
- sqlite
- web_service


### MemoryStore (Array)

#### Properties

- data: `list[dict]` A list of records
- error_handler: `callable` The error handler function
- key: `string` The field used as the `id` field.
- on_inserted: `callable(values, key)` Function executed after data is inserted.
- on_inserting: `callable(values)` Function called before an item is added to the store.
- on_loaded: `callable(result)` Function called after data is loaded to the store.
- on_loading: `callable(options)` Function called before data is loaded to the store.
- on_modified: `callable` Function called when data is added, updated, or removed.
- on_modifying: `callable` Function called before an item is added, updated, or removed.
- on_push: `callable(changes)` Function called before changes are pushed to the store.
- on_removed: `callable(key)` Function called after data is removed from the store.
- on_removing: `callable(key)` Function called before data item is removed from the store.
- on_updated: `callable(key, values)` Function called after a data item is updated in the store.
- on_updating: `callable(key, values)` Function called before item is updated to the store.

#### Methods

- `by_key(key)` Gets a data item with a specific key.
- `clear()` Clears all the stores associated data.
- `insert(values)` Add a data item to the store.
- `key()` Returns the id field used for the data store.
- `load(options)` Starts loading the data.
  - filter
  - sort
  - search_field
  - search_operator
  - search_value
  - select
  - skip
  - take
  - user_data
- `push(changes)` Push data changes to the store and notifies data source
  - type (insert, update, remove)
  - data: `object`
  - key: `any`
  - index: `number`
- `remove(key)` Remove the data item specific key from the store.
- `total_count(filter)` Gets the total count given optional filter
- `update(key, values)` Updates the data item with the specific key.

## DataSource

The object that provides an API for processing data from the underlying store

### Properties

- \_filter `string`: A filter expression.
- \_on_changed `callable`
- \_on_load_error `callable`
- \_on_loading_changed `callable`
- \_page_size `int`: The maximum number of records per page.
- \_paginate `bool`: Specifies if data is loaded all at once or in pages.
- \_post_process `callable`: A post processing function
- \_search_expr: `string[]`: The fields to search
- \_search_operator: `string`: The operator used for comparison
- \_search_value: `string`: The value in which to compare
- \_select: `string[]`: The fields to select from data objects
- \_sort: `object`: Data sorting properties
- \_store: `store`: The underlying store object

### Methods

- `cancel(operation_id)`: Cancels the operation with a specific identifier
- `dispose()`: Dispose all resources allocated to the datasource instance
- `filter(expr)`: Get or set the filter values property
- `is_last_page()`: Checks if count of items on current page is less than `page_size`
- `is_loaded()`: Checks if data is loaded in data source
- `is_loading()`: Checks if data is being loaded in the data source.
- `items()`: Gets an array of items in the current page.
- `key()`: Get the value of the underlying store's key property
- `load()`: Starts loading the data.
- `page_index(index)`: Gets or sets the current page index.
- `page_size(value)`: Get or set teh page size property.
- `paginate(value)`: Get or set the paginate property.
- `reload()`: Clear the currently loaded data source and call the `load()` method.
- `search_expr(expr)`: Get or set the search expression property.
- `search_operations(op)`: Get or set the search operation property.
- `search_value(value)`: Get or set the search value property.
- `sort(expr)`: Get or set the search value property.
- `store()`: Get the underlying store property.
- `total_count()`: Get the number of the data in the store after the last `load()` without paging.


### Events
- changed
- load_error
- loading_changed

## In Memory Database

```python
import sqlite3

# Create an in-memory SQLite database
conn = sqlite3.connect(":memory:")

# Use the connection as usual
cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
conn.commit()

cursor.execute("SELECT * FROM users")
print(cursor.fetchall())  # Output: [(1, 'Alice')]

conn.close()
```