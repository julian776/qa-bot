"""
Authentication router for user registration, login, and management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
from bson import ObjectId
import logging

from app.models.user import (
    UserCreate, UserLogin, UserResponse, Token, TokenData,
    UserUpdate, PasswordChange, UserInDB
)
from app.services.auth_service import auth_service
from app.database import db_config

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Dependency to get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = auth_service.decode_token(token)
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")

        if email is None or user_id is None:
            raise credentials_exception

    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise credentials_exception

    # Get user from database
    db = db_config.get_database()
    user = await db.users.find_one({"email": email})

    if user is None:
        raise credentials_exception

    # Convert to UserInDB model
    user_data = {
        **user,
        "id": str(user["_id"])
    }
    return UserInDB(**user_data)


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Dependency to ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user

    Args:
        user_data: User registration data

    Returns:
        Token with user information
    """
    try:
        db = db_config.get_database()

        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check username availability
        existing_username = await db.users.find_one({"username": user_data.username})
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Validate password strength
        is_valid, error_msg = auth_service.validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Hash password
        hashed_password = auth_service.get_password_hash(user_data.password)

        # Create user document
        user_doc = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }

        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)

        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user_data.email, "user_id": user_id}
        )

        # Return token and user info
        user_response = UserResponse(
            id=user_id,
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            is_active=True,
            is_verified=False,
            created_at=user_doc["created_at"],
            last_login=user_doc["last_login"]
        )

        logger.info(f"New user registered: {user_data.email}")

        return Token(access_token=access_token, user=user_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user with email and password

    Args:
        form_data: OAuth2 form with username (email) and password

    Returns:
        Token with user information
    """
    try:
        db = db_config.get_database()

        # Find user by email (username field in OAuth2 form)
        user = await db.users.find_one({"email": form_data.username})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not auth_service.verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )

        # Update last login
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        user_id = str(user["_id"])

        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user["email"], "user_id": user_id}
        )

        # Return token and user info
        user_response = UserResponse(
            id=user_id,
            email=user["email"],
            username=user["username"],
            full_name=user.get("full_name"),
            is_active=user.get("is_active", True),
            is_verified=user.get("is_verified", False),
            created_at=user["created_at"],
            last_login=datetime.utcnow()
        )

        logger.info(f"User logged in: {user['email']}")

        return Token(access_token=access_token, user=user_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/login/json", response_model=Token)
async def login_json(user_data: UserLogin):
    """
    Login user with JSON body (alternative to form-based login)

    Args:
        user_data: User login credentials

    Returns:
        Token with user information
    """
    try:
        db = db_config.get_database()

        # Find user by email
        user = await db.users.find_one({"email": user_data.email})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not auth_service.verify_password(user_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )

        # Update last login
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        user_id = str(user["_id"])

        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user["email"], "user_id": user_id}
        )

        # Return token and user info
        user_response = UserResponse(
            id=user_id,
            email=user["email"],
            username=user["username"],
            full_name=user.get("full_name"),
            is_active=user.get("is_active", True),
            is_verified=user.get("is_verified", False),
            created_at=user["created_at"],
            last_login=datetime.utcnow()
        )

        logger.info(f"User logged in (JSON): {user['email']}")

        return Token(access_token=access_token, user=user_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Returns:
        User information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Update current user's profile

    Args:
        user_update: Updated user data

    Returns:
        Updated user information
    """
    try:
        db = db_config.get_database()

        update_data = {}

        # Check email change
        if user_update.email and user_update.email != current_user.email:
            existing = await db.users.find_one({"email": user_update.email})
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            update_data["email"] = user_update.email

        # Check username change
        if user_update.username and user_update.username != current_user.username:
            existing = await db.users.find_one({"username": user_update.username})
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            update_data["username"] = user_update.username

        # Update full name
        if user_update.full_name is not None:
            update_data["full_name"] = user_update.full_name

        # Update password if provided
        if user_update.password:
            is_valid, error_msg = auth_service.validate_password_strength(user_update.password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            update_data["hashed_password"] = auth_service.get_password_hash(user_update.password)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )

        update_data["updated_at"] = datetime.utcnow()

        # Update user
        await db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": update_data}
        )

        # Get updated user
        updated_user = await db.users.find_one({"_id": ObjectId(current_user.id)})

        logger.info(f"User updated profile: {current_user.email}")

        return UserResponse(
            id=str(updated_user["_id"]),
            email=updated_user["email"],
            username=updated_user["username"],
            full_name=updated_user.get("full_name"),
            is_active=updated_user.get("is_active", True),
            is_verified=updated_user.get("is_verified", False),
            created_at=updated_user["created_at"],
            last_login=updated_user.get("last_login")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Change current user's password

    Args:
        password_data: Current and new password

    Returns:
        Success message
    """
    try:
        db = db_config.get_database()

        # Verify current password
        if not auth_service.verify_password(
            password_data.current_password,
            current_user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Validate new password
        is_valid, error_msg = auth_service.validate_password_strength(password_data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Hash new password
        new_hashed_password = auth_service.get_password_hash(password_data.new_password)

        # Update password
        await db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {
                "hashed_password": new_hashed_password,
                "updated_at": datetime.utcnow()
            }}
        )

        logger.info(f"Password changed for user: {current_user.email}")

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )
