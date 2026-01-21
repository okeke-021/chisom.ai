"""CLI for Chisom.ai management tasks"""
import asyncio
import click
from database.connection import init_db, get_async_db
from database.models import User
from auth.auth_service import AuthService
from scripts.scrape_templates import TemplateScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Chisom.ai CLI Management Tool"""
    pass


@cli.command()
def init():
    """Initialize the database"""
    click.echo("Initializing database...")
    try:
        init_db()
        click.echo("✅ Database initialized successfully!")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.option('--email', prompt=True, help='User email')
@click.option('--username', prompt=True, help='Username')
@click.option('--password', prompt=True, hide_input=True, help='Password')
@click.option('--pro', is_flag=True, help='Create as Pro user')
def create_user(email, username, password, pro):
    """Create a new user"""
    async def _create():
        async with get_async_db() as db:
            try:
                user = await AuthService.create_user(
                    db=db,
                    email=email,
                    username=username,
                    password=password,
                    is_pro=pro
                )
                tier = "Pro" if pro else "Free"
                click.echo(f"✅ User created successfully! Tier: {tier}")
                click.echo(f"User ID: {user.id}")
            except Exception as e:
                click.echo(f"❌ Error: {e}")
    
    asyncio.run(_create())


@cli.command()
@click.option('--username', prompt=True, help='Username to upgrade')
def upgrade_user(username):
    """Upgrade user to Pro"""
    async def _upgrade():
        async with get_async_db() as db:
            try:
                user = await AuthService.get_user_by_username(db, username)
                if not user:
                    click.echo(f"❌ User {username} not found")
                    return
                
                user.is_pro = True
                await db.commit()
                click.echo(f"✅ User {username} upgraded to Pro!")
            except Exception as e:
                click.echo(f"❌ Error: {e}")
    
    asyncio.run(_upgrade())


@cli.command()
def scrape_templates():
    """Scrape code templates from GitHub"""
    click.echo("Starting template scraping...")
    
    async def _scrape():
        scraper = TemplateScraper()
        try:
            await scraper.scrape_all()
            click.echo("✅ Template scraping completed!")
        except Exception as e:
            click.echo(f"❌ Error: {e}")
    
    asyncio.run(_scrape())


@cli.command()
@click.option('--query', prompt=True, help='Search query')
@click.option('--language', prompt=True, help='Programming language')
@click.option('--max-repos', default=5, help='Maximum repositories to scrape')
def search_repos(query, language, max_repos):
    """Search and add new repositories"""
    click.echo(f"Searching for {language} repositories...")
    
    async def _search():
        scraper = TemplateScraper()
        try:
            await scraper.search_and_add_repos(query, language, max_repos)
            click.echo("✅ Repository search completed!")
        except Exception as e:
            click.echo(f"❌ Error: {e}")
    
    asyncio.run(_search())


@cli.command()
def stats():
    """Show database statistics"""
    async def _stats():
        async with get_async_db() as db:
            from sqlalchemy import func, select
            from database.models import User, Project, CodeTemplate
            
            try:
                # Count users
                user_count = await db.execute(select(func.count(User.id)))
                users = user_count.scalar()
                
                # Count projects
                project_count = await db.execute(select(func.count(Project.id)))
                projects = project_count.scalar()
                
                # Count templates
                template_count = await db.execute(select(func.count(CodeTemplate.id)))
                templates = template_count.scalar()
                
                click.echo("\n📊 Database Statistics")
                click.echo("=" * 40)
                click.echo(f"Users: {users}")
                click.echo(f"Projects: {projects}")
                click.echo(f"Code Templates: {templates}")
                click.echo("=" * 40)
                
            except Exception as e:
                click.echo(f"❌ Error: {e}")
    
    asyncio.run(_stats())


@cli.command()
@click.option('--username', prompt=True, help='Username')
def reset_rate_limit(username):
    """Reset rate limit for a user"""
    async def _reset():
        async with get_async_db() as db:
            from database.models import RateLimit
            from sqlalchemy import delete
            
            try:
                user = await AuthService.get_user_by_username(db, username)
                if not user:
                    click.echo(f"❌ User {username} not found")
                    return
                
                # Delete rate limit records for user
                await db.execute(
                    delete(RateLimit).where(RateLimit.user_id == user.id)
                )
                await db.commit()
                
                click.echo(f"✅ Rate limit reset for {username}")
            except Exception as e:
                click.echo(f"❌ Error: {e}")
    
    asyncio.run(_reset())


@cli.command()
def run():
    """Run the Chainlit application"""
    import subprocess
    
    click.echo("Starting Chisom.ai...")
    try:
        subprocess.run(
            ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"],
            check=True
        )
    except KeyboardInterrupt:
        click.echo("\n👋 Shutting down...")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


if __name__ == "__main__":
    cli()
