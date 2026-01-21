"""Authentication and authorization service"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, RateLimit
from config import settings
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handle authentication operations"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    async def create_user(
        db: AsyncSession, 
        email: str, 
        username: str, 
        password: str,
        is_pro: bool = False
    ) -> User:
        """Create a new user"""
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_pro=is_pro
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created user: {username}")
        return user
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None


class RateLimitService:
    """Handle rate limiting"""
    
    @staticmethod
    async def check_rate_limit(db: AsyncSession, user: User) -> tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit
        Returns: (is_allowed, used_requests, max_requests)
        """
        today = datetime.utcnow().date()
        
        # Get today's rate limit record
        result = await db.execute(
            select(RateLimit).where(
                RateLimit.user_id == user.id,
                RateLimit.date >= datetime.combine(today, datetime.min.time())
            )
        )
        rate_limit = result.scalar_one_or_none()
        
        # Determine max requests based on user tier
        max_requests = (
            settings.pro_tier_daily_limit if user.is_pro 
            else settings.free_tier_daily_limit
        )
        
        if not rate_limit:
            # Create new rate limit record
            rate_limit = RateLimit(
                user_id=user.id,
                date=datetime.utcnow(),
                request_count=0
            )
            db.add(rate_limit)
            await db.commit()
            await db.refresh(rate_limit)
        
        # Check limit
        is_allowed = rate_limit.request_count < max_requests
        
        return is_allowed, rate_limit.request_count, max_requests
    
    @staticmethod
    async def increment_rate_limit(db: AsyncSession, user: User):
        """Increment user's rate limit counter"""
        today = datetime.utcnow().date()
        
        result = await db.execute(
            select(RateLimit).where(
                RateLimit.user_id == user.id,
                RateLimit.date >= datetime.combine(today, datetime.min.time())
            )
        )
        rate_limit = result.scalar_one_or_none()
        
        if rate_limit:
            rate_limit.request_count += 1
            await db.commit()
            logger.info(f"Incremented rate limit for user {user.username}: {rate_limit.request_count}")
        else:
            logger.warning(f"Rate limit record not found for user {user.username}")
