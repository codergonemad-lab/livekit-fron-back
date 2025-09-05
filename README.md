# LiveKit Video Calling Backend

A comprehensive backend API for video calling applications built with FastAPI and LiveKit, featuring user management, room management, and real-time video calling capabilities.

## Features

- **User Management**: Registration, authentication, and user profiles
- **Room Management**: Create, join, leave, and delete video call rooms
- **LiveKit Integration**: Real-time video calling with LiveKit Cloud
- **JWT Authentication**: Secure token-based authentication
- **PostgreSQL Database**: Persistent data storage
- **REST API**: Complete RESTful API with auto-generated documentation

## Architecture

### High-Level Components

1. **User Management**

   - User registration and login
   - JWT token-based authentication
   - User profile management

2. **Room Management**

   - Create video call rooms
   - Join/leave rooms
   - Track participants
   - Room metadata storage

3. **LiveKit Integration**
   - Generate access tokens for LiveKit
   - Create/delete rooms in LiveKit Cloud
   - Real-time participant tracking

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Video Calling**: LiveKit Cloud
- **Migrations**: Alembic
- **Server**: Uvicorn

## Prerequisites

- Python 3.8+
- PostgreSQL database
- LiveKit Cloud account (or self-hosted LiveKit server)

## Installation

1. **Clone and setup the project:**

   ```bash
   cd /home/codergonemad/Desktop/project
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database:**

   ```sql
   CREATE DATABASE livekit_db;
   CREATE USER livekit_user WITH PASSWORD 'singhkunj26';
   GRANT ALL PRIVILEGES ON DATABASE livekit_db TO livekit_user;
   ```

5. **Configure environment variables:**
   The `.env` file is already configured with your settings. Ensure your PostgreSQL database is running.

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

## Running the Application

### Development Mode

```bash
python -m app.main
```

### Using Uvicorn directly

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication (`/auth`)

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information

### Rooms (`/rooms`)

- `POST /rooms/` - Create a new room
- `GET /rooms/` - List all active rooms
- `GET /rooms/{room_id}` - Get specific room details
- `POST /rooms/{room_id}/join` - Join a room and get LiveKit token
- `POST /rooms/{room_id}/leave` - Leave a room
- `DELETE /rooms/{room_id}` - Delete a room (creator only)
- `GET /rooms/{room_id}/participants` - Get room participants

### Users (`/users`)

- `GET /users/` - List all users
- `GET /users/{user_id}` - Get specific user

## Usage Examples

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_doe",
       "email": "john@example.com",
       "password": "secure_password",
       "full_name": "John Doe"
     }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=john_doe&password=secure_password"
```

### 3. Create a Room

```bash
curl -X POST "http://localhost:8000/rooms/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{
       "name": "My Video Call",
       "description": "A test video call room",
       "max_participants": 10
     }'
```

### 4. Join a Room

```bash
curl -X POST "http://localhost:8000/rooms/1/join" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Database Schema

### Users Table

- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

### Rooms Table

- `id`: Primary key
- `name`: Room display name
- `room_id`: Unique LiveKit room identifier
- `description`: Room description
- `creator_id`: Foreign key to users table
- `is_active`: Room status
- `max_participants`: Maximum allowed participants
- `created_at`, `updated_at`: Timestamps

### Room Participants Table

- `id`: Primary key
- `room_id`: Foreign key to rooms table
- `user_id`: Foreign key to users table
- `joined_at`, `left_at`: Participation timestamps
- `is_connected`: Current connection status

## LiveKit Integration

This backend integrates with LiveKit for real-time video calling:

1. **Room Creation**: When you create a room via the API, it's also created in LiveKit
2. **Token Generation**: When joining a room, the backend generates a LiveKit access token
3. **Participant Tracking**: The backend tracks participants both locally and via LiveKit APIs

### LiveKit Configuration

Your LiveKit settings in `.env`:

- `LIVEKIT_URL`: Your LiveKit server URL
- `LIVEKIT_API_KEY`: Your API key
- `LIVEKIT_API_SECRET`: Your API secret

## Security Considerations

1. **JWT Tokens**: Secure token-based authentication with configurable expiration
2. **Password Hashing**: Bcrypt hashing for password security
3. **Database Security**: Use strong database credentials in production
4. **CORS**: Configure appropriate CORS origins for production
5. **Environment Variables**: Keep sensitive data in environment variables

## Development

### Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

### Running Tests

```bash
pytest  # After adding test files
```

## Production Deployment

1. **Environment Variables**: Update all security-sensitive values
2. **Database**: Use a production PostgreSQL instance
3. **CORS**: Configure specific allowed origins
4. **HTTPS**: Enable HTTPS/TLS
5. **Process Manager**: Use gunicorn or similar for production

Example production command:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Ensure PostgreSQL is running and credentials are correct
2. **LiveKit Token Error**: Verify your LiveKit credentials and URL
3. **Authentication Error**: Check JWT secret key configuration

### Logs

Enable debug logging by setting `DEBUG=True` in your environment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review the troubleshooting section
3. Check LiveKit documentation: https://docs.livekit.io/
