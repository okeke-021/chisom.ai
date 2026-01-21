"""Main Chainlit application for Chisom.ai"""
import chainlit as cl
from chainlit.types import ThreadDict
from typing import Optional, Dict
import asyncio
import logging
from datetime import datetime

from config import settings
from database.connection import get_async_db, init_db
from database.models import User, Project, ChatSession, ChatMessage
from auth.auth_service import AuthService, RateLimitService
from services.github_service import GitHubService
from services.code_quality_service import CodeQualityService
from services.vector_store_service import VectorStoreService
from agents.app_generator_agent import AppGeneratorAgent

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize services
github_service = GitHubService()
vector_store = VectorStoreService()
code_quality = CodeQualityService()
app_generator = AppGeneratorAgent()


@cl.password_auth_callback
async def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """Authentication callback"""
    try:
        async with get_async_db() as db:
            user = await AuthService.authenticate_user(db, username, password)
            
            if user:
                return cl.User(
                    identifier=user.id,
                    metadata={
                        "email": user.email,
                        "username": user.username,
                        "is_pro": user.is_pro
                    }
                )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
    
    return None


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session"""
    user = cl.user_session.get("user")
    
    # Welcome message with starter options
    await cl.Message(
        content=f"# Welcome to Chisom.ai! 🚀\n\n"
                f"I'm your AI agent builder. I can help you create complete web applications "
                f"from natural language descriptions.\n\n"
                f"**What I can do:**\n"
                f"- Generate production-ready code\n"
                f"- Select optimal tech stacks\n"
                f"- Create Docker configurations\n"
                f"- Push to GitHub automatically\n"
                f"- Preview your application\n\n"
                f"Ready to build something amazing? 💡",
        author="Chisom.ai"
    ).send()
    
    # Check rate limit
    try:
        async with get_async_db() as db:
            user_obj = await AuthService.get_user_by_username(db, user.metadata["username"])
            is_allowed, used, max_requests = await RateLimitService.check_rate_limit(db, user_obj)
            
            tier = "Pro" if user_obj.is_pro else "Free"
            await cl.Message(
                content=f"📊 **Your Plan:** {tier}\n"
                        f"**Requests Today:** {used}/{max_requests}",
                author="System"
            ).send()
            
            if not is_allowed:
                await cl.Message(
                    content="⚠️ You've reached your daily limit. "
                            "Upgrade to Pro for 30 requests/day!",
                    author="System"
                ).send()
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
    
    # Store user session data
    cl.user_session.set("app_generator", app_generator)
    cl.user_session.set("github_service", github_service)
    cl.user_session.set("vector_store", vector_store)
    
    # Create chat session in database
    try:
        async with get_async_db() as db:
            user_obj = await AuthService.get_user_by_username(db, user.metadata["username"])
            chat_session = ChatSession(user_id=user_obj.id)
            db.add(chat_session)
            await db.commit()
            cl.user_session.set("chat_session_id", chat_session.id)
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    user = cl.user_session.get("user")
    
    # Check rate limit
    try:
        async with get_async_db() as db:
            user_obj = await AuthService.get_user_by_username(db, user.metadata["username"])
            is_allowed, used, max_requests = await RateLimitService.check_rate_limit(db, user_obj)
            
            if not is_allowed:
                await cl.Message(
                    content="⚠️ Daily limit reached! Upgrade to Pro for more requests.",
                    author="System"
                ).send()
                return
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        return
    
    # Save message to database
    try:
        async with get_async_db() as db:
            session_id = cl.user_session.get("chat_session_id")
            chat_msg = ChatMessage(
                session_id=session_id,
                role="user",
                content=message.content
            )
            db.add(chat_msg)
            await db.commit()
    except Exception as e:
        logger.error(f"Error saving message: {e}")
    
    # Process message
    app_gen = cl.user_session.get("app_generator")
    
    # Create step for progress tracking
    async with cl.Step(name="Generating Application") as step:
        step.input = message.content
        
        try:
            # Generate application
            result = await app_gen.generate_app(message.content)
            
            if result["errors"]:
                error_msg = "\n".join(result["errors"])
                await cl.Message(
                    content=f"⚠️ Encountered some issues:\n{error_msg}",
                    author="System"
                ).send()
            
            # Display tech stack
            tech_stack_msg = "## 🛠️ Selected Tech Stack\n\n"
            for key, value in result["tech_stack"].items():
                tech_stack_msg += f"- **{key.title()}:** {value}\n"
            
            await cl.Message(
                content=tech_stack_msg,
                author="Chisom.ai"
            ).send()
            
            # Create GitHub repository
            try:
                repo_name = f"chisom-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                repo_url = github_service.create_repository(
                    repo_name=repo_name,
                    description=message.content
                )
                
                # Commit files
                files = {**result["generated_files"]}
                files["Dockerfile"] = result["dockerfile"]
                files["docker-compose.yml"] = result["docker_compose"]
                files["README.md"] = result["readme"]
                
                github_service.commit_files(
                    repo_name=repo_name,
                    files=files,
                    commit_message="Initial commit by Chisom.ai"
                )
                
                await cl.Message(
                    content=f"✅ **GitHub Repository Created!**\n\n"
                            f"🔗 [{repo_url}]({repo_url})",
                    author="Chisom.ai"
                ).send()
                
                # Save project to database
                async with get_async_db() as db:
                    user_obj = await AuthService.get_user_by_username(
                        db, 
                        user.metadata["username"]
                    )
                    project = Project(
                        user_id=user_obj.id,
                        name=repo_name,
                        description=message.content,
                        tech_stack=result["tech_stack"],
                        github_repo_url=repo_url,
                        github_repo_name=repo_name,
                        status="completed"
                    )
                    db.add(project)
                    await db.commit()
                
            except Exception as e:
                logger.error(f"GitHub error: {e}")
                await cl.Message(
                    content=f"⚠️ Error creating GitHub repo: {str(e)}",
                    author="System"
                ).send()
            
            # Display README
            await cl.Message(
                content=f"## 📖 README\n\n{result['readme']}",
                author="Chisom.ai"
            ).send()
            
            step.output = "Application generated successfully!"
            
            # Increment rate limit
            async with get_async_db() as db:
                user_obj = await AuthService.get_user_by_username(
                    db, 
                    user.metadata["username"]
                )
                await RateLimitService.increment_rate_limit(db, user_obj)
            
        except Exception as e:
            logger.error(f"Error generating app: {e}")
            step.output = f"Error: {str(e)}"
            await cl.Message(
                content=f"❌ An error occurred: {str(e)}",
                author="System"
            ).send()
    
    # Save assistant response
    try:
        async with get_async_db() as db:
            session_id = cl.user_session.get("chat_session_id")
            chat_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                content="Application generated",
                metadata={"tech_stack": result["tech_stack"]}
            )
            db.add(chat_msg)
            await db.commit()
    except Exception as e:
        logger.error(f"Error saving assistant message: {e}")


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    """Resume previous chat session"""
    user = cl.user_session.get("user")
    
    await cl.Message(
        content="Welcome back! Resuming your previous session...",
        author="Chisom.ai"
    ).send()
    
    # Load chat history
    try:
        async with get_async_db() as db:
            user_obj = await AuthService.get_user_by_username(db, user.metadata["username"])
            # Load messages and display
            # Implementation depends on how you want to display history
    except Exception as e:
        logger.error(f"Error resuming chat: {e}")


@cl.action_callback("upgrade_to_pro")
async def on_action(action: cl.Action):
    """Handle upgrade to pro action"""
    await cl.Message(
        content="To upgrade to Pro, please visit: [Upgrade Page](https://chisom.ai/upgrade)",
        author="System"
    ).send()


# Startup event
@cl.on_startup
async def on_startup():
    """Initialize application on startup"""
    logger.info("Starting Chisom.ai...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")


if __name__ == "__main__":
    logger.info("Running Chisom.ai")
    # Chainlit will handle the server startup
