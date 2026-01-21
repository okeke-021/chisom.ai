"""Extended Chainlit features for Chisom.ai"""
import chainlit as cl
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


# Starter Templates
@cl.set_starters
async def set_starters():
    """Set starter prompts for users"""
    return [
        cl.Starter(
            label="Todo App",
            message="Create a todo application with React, authentication, and a clean UI",
            icon="/public/icons/todo.svg"
        ),
        cl.Starter(
            label="E-commerce Store",
            message="Build an e-commerce platform with product catalog, cart, and Stripe integration",
            icon="/public/icons/shop.svg"
        ),
        cl.Starter(
            label="Blog Platform",
            message="Create a blog with markdown support, comments, and admin dashboard",
            icon="/public/icons/blog.svg"
        ),
        cl.Starter(
            label="Dashboard Analytics",
            message="Build a data analytics dashboard with charts, filters, and real-time updates",
            icon="/public/icons/chart.svg"
        )
    ]


# Chat Actions
@cl.action_callback("view_project")
async def view_project(action: cl.Action):
    """View project details"""
    project_id = action.value
    await cl.Message(
        content=f"Loading project {project_id}...",
        author="System"
    ).send()


@cl.action_callback("delete_project")
async def delete_project(action: cl.Action):
    """Delete project"""
    project_id = action.value
    
    # Confirm deletion
    res = await cl.AskActionMessage(
        content="Are you sure you want to delete this project?",
        actions=[
            cl.Action(name="confirm", value="yes", label="✅ Yes, delete it"),
            cl.Action(name="cancel", value="no", label="❌ Cancel")
        ]
    ).send()
    
    if res and res.get("value") == "yes":
        # Delete project logic here
        await cl.Message(
            content="Project deleted successfully",
            author="System"
        ).send()


@cl.action_callback("upgrade_plan")
async def upgrade_plan(action: cl.Action):
    """Upgrade to Pro plan"""
    await cl.Message(
        content="# Upgrade to Pro 🚀\n\n"
                "**Pro Benefits:**\n"
                "- 30 requests per day (vs 5 on free)\n"
                "- Priority processing\n"
                "- Advanced templates\n"
                "- Email support\n\n"
                "**Price:** $29/month\n\n"
                "[Upgrade Now](https://chisom.ai/upgrade)",
        author="System"
    ).send()


# Chat Commands
@cl.on_command("/projects")
async def list_projects():
    """List user's projects"""
    user = cl.user_session.get("user")
    
    # Get projects from database
    projects = []  # Query database here
    
    if not projects:
        await cl.Message(
            content="You don't have any projects yet. Start building!",
            author="System"
        ).send()
        return
    
    # Create elements for each project
    elements = []
    for project in projects:
        elements.append(
            cl.Text(
                name=project['name'],
                content=f"**{project['name']}**\n{project['description']}\n"
                        f"🔗 [View on GitHub]({project['github_url']})",
                display="inline"
            )
        )
    
    await cl.Message(
        content="# Your Projects",
        elements=elements,
        author="System"
    ).send()


@cl.on_command("/help")
async def show_help():
    """Show help message"""
    await cl.Message(
        content="""
# Chisom.ai Help 💡

## Commands
- `/projects` - List your projects
- `/help` - Show this help message
- `/upgrade` - Upgrade to Pro
- `/stats` - View your usage statistics

## How to Use
1. Describe your app idea in natural language
2. AI will generate complete codebase
3. Review tech stack and architecture
4. Get GitHub repository with all files
5. Deploy to your infrastructure

## Examples
- "Create a todo app with authentication"
- "Build an e-commerce store with Stripe"
- "Make a blog platform with markdown support"

## Support
- Documentation: https://docs.chisom.ai
- Discord: https://discord.gg/chisom-ai
- Email: support@chisom.ai
        """,
        author="System"
    ).send()


@cl.on_command("/upgrade")
async def upgrade_command():
    """Upgrade to Pro command"""
    await upgrade_plan(cl.Action(name="upgrade_plan", value=""))


@cl.on_command("/stats")
async def show_stats():
    """Show user statistics"""
    user = cl.user_session.get("user")
    
    # Get stats from database
    await cl.Message(
        content="""
# Your Statistics 📊

**Plan:** Free Tier
**Requests Today:** 3/5
**Total Projects:** 7
**Templates Used:** 15

Upgrade to Pro for 30 requests/day!
[Upgrade Now](https://chisom.ai/upgrade)
        """,
        author="System"
    ).send()


# File Upload Handler
@cl.on_file_upload(accept=["text/plain", "application/json", "text/markdown"])
async def handle_file_upload(file: cl.File):
    """Handle file uploads"""
    content = file.content.decode('utf-8')
    
    await cl.Message(
        content=f"📄 File uploaded: **{file.name}**\n\n"
                f"I can help you:\n"
                f"- Convert this to a different format\n"
                f"- Generate code based on this spec\n"
                f"- Create tests for this\n\n"
                f"What would you like to do?",
        author="System"
    ).send()


# Chat Settings
@cl.on_settings_update
async def setup_agent(settings):
    """Update settings"""
    logger.info(f"Settings updated: {settings}")
    
    await cl.Message(
        content="Settings updated successfully!",
        author="System"
    ).send()


# User Session Management
async def setup_user_session(user):
    """Setup user session with preferences"""
    cl.user_session.set("preferences", {
        "theme": "dark",
        "language": "en",
        "notifications": True
    })
    
    cl.user_session.set("context", {
        "recent_projects": [],
        "favorite_frameworks": [],
        "tech_preferences": {}
    })


# Element Display Functions
async def display_code_preview(code: str, language: str, filename: str):
    """Display code preview"""
    await cl.Message(
        content=f"## 📄 {filename}",
        author="Chisom.ai",
        elements=[
            cl.Code(
                name=filename,
                content=code,
                language=language
            )
        ]
    ).send()


async def display_project_structure(structure: Dict):
    """Display project structure"""
    tree_str = "```\n"
    for path, desc in structure.items():
        depth = path.count('/')
        indent = "  " * depth
        name = path.split('/')[-1]
        tree_str += f"{indent}├── {name}\n"
    tree_str += "```"
    
    await cl.Message(
        content=f"## 📁 Project Structure\n\n{tree_str}",
        author="Chisom.ai"
    ).send()


async def display_tech_stack(tech_stack: Dict):
    """Display selected tech stack with icons"""
    elements = []
    
    for key, value in tech_stack.items():
        elements.append(
            cl.Text(
                name=key,
                content=f"**{key.title()}:** {value}",
                display="inline"
            )
        )
    
    await cl.Message(
        content="## 🛠️ Selected Tech Stack",
        elements=elements,
        author="Chisom.ai"
    ).send()


async def show_generation_progress(steps: List[str]):
    """Show generation progress with steps"""
    async with cl.Step(name="Generating Application", type="tool") as parent_step:
        for i, step_name in enumerate(steps, 1):
            async with cl.Step(name=step_name, parent_id=parent_step.id) as step:
                step.output = f"Step {i} completed"
                await cl.sleep(1)  # Simulate work


# Chat Profile Management
@cl.set_chat_profiles
async def chat_profiles():
    """Set chat profiles for different use cases"""
    return [
        cl.ChatProfile(
            name="General",
            markdown_description="General purpose app generation",
            icon="/public/icons/general.svg"
        ),
        cl.ChatProfile(
            name="Frontend",
            markdown_description="Specialized in frontend applications",
            icon="/public/icons/frontend.svg"
        ),
        cl.ChatProfile(
            name="Backend",
            markdown_description="Specialized in backend services",
            icon="/public/icons/backend.svg"
        ),
        cl.ChatProfile(
            name="Full-Stack",
            markdown_description="Complete full-stack applications",
            icon="/public/icons/fullstack.svg"
        )
    ]


# Assistant Messages
async def send_assistant_message(content: str, elements: Optional[List] = None):
    """Send formatted assistant message"""
    msg = cl.Message(
        content=content,
        author="Chisom.ai",
        elements=elements or []
    )
    await msg.send()


# Error Handling
async def display_error(error: Exception, context: str = ""):
    """Display user-friendly error message"""
    await cl.Message(
        content=f"❌ **Error:** {str(error)}\n\n"
                f"{context}\n\n"
                f"Please try again or contact support if the issue persists.",
        author="System"
    ).send()
