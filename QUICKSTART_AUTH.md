# Quick Start - Authentication System

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies

```bash
# Backend
cd backend
pip install python-jose passlib bcrypt
```

### Step 2: Set SECRET_KEY

Add to `backend/.env`:

```bash
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=9vK3xR7pQ2mL8nF4wH6yJ1sT5bN0zC9aE3dG8fV2hU1k

# Your existing vars...
OPENAI_API_KEY=...
MONGODB_URL=mongodb://localhost:27017
```

### Step 3: Start Everything

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 4: Create Your Account

1. Open http://localhost:5173
2. Click "Regístrate aquí"
3. Fill in:
   - Email: `your@email.com`
   - Username: `yourusername`
   - Password: `SecurePass123` (min 8 chars, uppercase, lowercase, numbers)
4. Click "Crear Cuenta"

**Done!** You're logged in and ready to chat.

---

## 🎯 What You Get

### Login Screen
- Beautiful gradient UI
- Email + password login
- Switch to register

### Register Screen
- Create new account
- Email, username, password
- Optional full name
- Password validation

### User Profile
- Click 👤 button in top bar
- View profile info
- Edit username, email, full name
- Logout button

### Protected App
- Must be logged in to access
- JWT token authentication
- Automatic token refresh
- Logout clears all data

---

## 📋 Quick Test

### Test Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

You should get back a token and user object.

---

## ⚠️ Common Issues

### "ModuleNotFoundError: No module named 'jose'"
```bash
pip install python-jose[cryptography]
```

### "ModuleNotFoundError: No module named 'passlib'"
```bash
pip install passlib[bcrypt]
```

### "Could not validate credentials"
- Logout and login again
- Check if SECRET_KEY is set in .env
- Clear browser localStorage

### "Email already registered"
- Use a different email
- OR login with existing account

---

## 📖 Full Documentation

For complete details, see:
- **AUTH_COMPLETE_GUIDE.md** - Full setup and API reference
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **DEPLOYMENT_GUIDE.md** - Production deployment

---

## ✨ Features Included

✅ User registration with validation
✅ Secure login (JWT tokens)
✅ Profile management
✅ Password requirements enforcement
✅ Logout functionality
✅ Protected routes
✅ Beautiful UI
✅ Responsive design
✅ Error handling
✅ Token persistence

---

## 🎉 You're Ready!

Your app now has:
- Multi-user support
- Secure authentication
- User profiles
- Protected data

Start chatting! 🤖💬
