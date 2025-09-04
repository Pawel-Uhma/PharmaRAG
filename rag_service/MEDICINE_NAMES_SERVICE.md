# Medicine Names Service

This service provides paginated access to medicine names from the `medicine_names_minimal.json` file.

## Features

- **Paginated Medicine Names**: Get medicine names with configurable page size
- **Search Functionality**: Search medicine names by query string
- **Total Count**: Get the total number of available medicine names
- **Error Handling**: Comprehensive error handling and logging
- **Performance Optimized**: Efficient pagination with reasonable limits

## Endpoints

### 1. GET /medicine-names/paginated

Get paginated medicine names.

**URL Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 20, max: 100)

**Example Request:**
```
GET http://localhost:8000/medicine-names/paginated?page=1&page_size=20
```

**Response:**
```json
{
  "names": [
    "2KC - tabletki",
    "4 Lacti BABY - krople",
    "4Flex - proszek",
    // ... more names
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 296,
    "total_items": 5912,
    "has_next": true,
    "has_previous": false
  }
}
```

### 2. GET /medicine-names/search

Search medicine names by query with pagination.

**URL Parameters:**
- `query` (required): Search query string
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 20, max: 100)

**Example Request:**
```
GET http://localhost:8000/medicine-names/search?query=aspirin&page=1&page_size=10
```

**Response:**
```json
{
  "names": [
    "Aspirin - tabletki",
    "Aspirin Cardio - tabletki",
    // ... matching names
  ],
  "query": "aspirin",
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_pages": 1,
    "total_items": 5,
    "has_next": false,
    "has_previous": false
  }
}
```

### 3. GET /medicine-names/count

Get the total count of medicine names.

**Example Request:**
```
GET http://localhost:8000/medicine-names/count
```

**Response:**
```json
{
  "total_count": 5912
}
```

## Usage Examples

### Frontend Integration

```typescript
// Example React hook usage
const useMedicineNames = () => {
  const [names, setNames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({});

  const fetchNames = async (page = 1, pageSize = 20) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/medicine-names/paginated?page=${page}&page_size=${pageSize}`
      );
      const data = await response.json();
      setNames(data.names);
      setPagination(data.pagination);
    } catch (error) {
      console.error('Error fetching medicine names:', error);
    } finally {
      setLoading(false);
    }
  };

  return { names, loading, pagination, fetchNames };
};
```

### Search Example

```typescript
const searchMedicineNames = async (query: string, page = 1, pageSize = 20) => {
  const response = await fetch(
    `http://localhost:8000/medicine-names/search?query=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`
  );
  return await response.json();
};
```

## Error Handling

The service includes comprehensive error handling:

- **File Not Found**: Returns 500 error if JSON file is missing
- **Invalid Parameters**: Automatically corrects invalid page/page_size values
- **Service Not Initialized**: Returns 500 error if service fails to initialize
- **Search Errors**: Handles search query errors gracefully

## Performance Considerations

- **Page Size Limit**: Maximum page size is 100 to prevent performance issues
- **Efficient Loading**: Medicine names are loaded once at service startup
- **Memory Optimized**: Uses efficient list slicing for pagination
- **Case-Insensitive Search**: Optimized search with case-insensitive matching

## Testing

Run the test script to verify all endpoints:

```bash
cd rag_service
python test_medicine_names.py
```

## Integration with RAG Service

The Medicine Names Service is fully integrated into the main RAG service:

- **Automatic Initialization**: Service starts with the main RAG service
- **Shared Logging**: Uses the same logging configuration
- **CORS Support**: All endpoints support CORS for frontend integration
- **Health Monitoring**: Service status is included in health checks

## Data Source

The service reads from `medicine_names_minimal.json` which contains:
- `names`: Array of medicine names
- `total_count`: Total number of medicine names

The file is automatically loaded at service startup and cached in memory for optimal performance.
