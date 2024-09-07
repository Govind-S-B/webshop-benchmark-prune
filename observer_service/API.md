# Observer Service API Documentation

## Base URL
`http://<host>:5000`

## Endpoints

### Start Observer
**URL:** `/start`  
**Method:** `POST`  
**Description:** Starts the observer task if it is not already running.

**Request Body:**
```json
{
  "start": <integer>,  // Starting session ID (default: 0)
  "end": <integer>     // Ending session ID (default: 1000)
}
```

**Responses:**
- `200 OK` - Observer task started.
- `400 Bad Request` - Observer task is already running.

### Stop Observer
**URL:** `/stop`  
**Method:** `POST`  
**Description:** Stops the observer task gracefully. This will abandond the currently running session it was observing. So remember to trim to clean that up if stopping a session

**Responses:**
- `200 OK` - Observer task stopped.

### Clean Logs
**URL:** `/clean`  
**Method:** `POST`  
**Description:** Cleans the log directory by deleting all files.

**Responses:**
- `200 OK` - Log directory cleaned.

### Save Session
**URL:** `/save`  
**Method:** `POST`  
**Description:** Saves the current logs with a given name by moving the contents of the log directory to a new location.

**Request Body:**
```json
{
  "name": <string>  // Name to save the session logs (default: "default_name")
}
```

**Responses:**
- `200 OK` - Session saved with the given name.

### Get Session
**URL:** `/get`  
**Method:** `GET`  
**Description:** Compresses and provides the saved session logs as a zip file.

**Query Parameters:**
- `name` (string) - Name of the saved session logs to retrieve (default: "default_name").

**Responses:**
- `200 OK` - Returns the zip file of the saved session logs.

### Get Status
**URL:** `/status`  
**Method:** `GET`  
**Description:** Returns the current status of the observer, including whether it is running and the current session details.

**Responses:**
- `200 OK` - Returns the current status of the observer.

## Example Usage

### Start Observer
```bash
curl -X POST http://<host>:5000/start -H "Content-Type: application/json" -d '{"start": 0, "end": 1000}'
```

### Stop Observer
```bash
curl -X POST http://<host>:5000/stop
```

### Clean Logs
```bash
curl -X POST http://<host>:5000/clean
```

### Save Session
```bash
curl -X POST http://<host>:5000/save -H "Content-Type: application/json" -d '{"name": "session_name"}'
```

### Get Session
```bash
curl -X GET "http://<host>:5000/get?name=session_name"
```

### Get Status
```bash
curl -X GET http://<host>:5000/status
```