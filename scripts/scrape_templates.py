"""Script to scrape and process code templates from GitHub"""
import asyncio
from typing import List, Dict
import logging
from sqlalchemy import select

from config import settings
from database.connection import get_async_db
from database.models import CodeTemplate
from services.github_service import GitHubService
from services.code_quality_service import CodeQualityService
from services.vector_store_service import VectorStoreService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateScraper:
    """Scrape and process code templates from approved GitHub repositories"""
    
    def __init__(self):
        self.github = GitHubService()
        self.code_quality = CodeQualityService()
        self.vector_store = VectorStoreService()
        
        # Approved repositories and frameworks
        self.approved_repos = {
            "react": [
                "facebook/react",
                "vercel/next.js",
                "remix-run/remix"
            ],
            "vue": [
                "vuejs/core",
                "nuxt/nuxt"
            ],
            "python": [
                "tiangolo/fastapi",
                "pallets/flask",
                "django/django"
            ],
            "typescript": [
                "microsoft/TypeScript",
                "typescript-eslint/typescript-eslint"
            ]
        }
    
    async def scrape_all(self):
        """Scrape templates from all approved repositories"""
        logger.info("Starting template scraping process")
        
        total_templates = 0
        
        for framework, repos in self.approved_repos.items():
            logger.info(f"Processing {framework} repositories")
            
            for repo in repos:
                try:
                    count = await self.scrape_repository(repo, framework)
                    total_templates += count
                    logger.info(f"Scraped {count} templates from {repo}")
                except Exception as e:
                    logger.error(f"Error scraping {repo}: {e}")
        
        logger.info(f"Total templates scraped: {total_templates}")
    
    async def scrape_repository(self, repo_name: str, framework: str) -> int:
        """Scrape templates from a single repository"""
        logger.info(f"Scraping repository: {repo_name}")
        
        # Get code files from repository
        code_files = self.github.scrape_repository_code(repo_name)
        
        templates_added = 0
        
        for file_path, code_content in code_files.items():
            try:
                # Determine language from file extension
                language = self._get_language(file_path)
                
                # Validate syntax
                is_valid, error = self.code_quality.validate_syntax(code_content, language)
                if not is_valid:
                    logger.warning(f"Syntax error in {file_path}: {error}")
                    continue
                
                # Analyze code quality
                is_quality, issues, quality_score = await self._analyze_quality(
                    code_content, 
                    language
                )
                
                # Filter by quality score
                if quality_score < 70:
                    logger.info(f"Skipping {file_path} due to low quality score: {quality_score}")
                    continue
                
                # Extract metadata
                metadata = self._extract_metadata(file_path, code_content, framework)
                metadata['quality_score'] = quality_score
                metadata['source_repo'] = repo_name
                
                # Categorize
                category = self._categorize_code(file_path, code_content)
                
                # Save to database and vector store
                await self._save_template(
                    file_path=file_path,
                    code=code_content,
                    framework=framework,
                    category=category,
                    metadata=metadata,
                    quality_score=quality_score,
                    source_url=f"https://github.com/{repo_name}/blob/main/{file_path}"
                )
                
                templates_added += 1
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        return templates_added
    
    async def _analyze_quality(self, code: str, language: str) -> tuple:
        """Analyze code quality"""
        if language == 'python':
            return self.code_quality.analyze_python(code)
        elif language in ['javascript', 'typescript']:
            return self.code_quality.analyze_javascript(code)
        return True, [], 80.0
    
    def _get_language(self, file_path: str) -> str:
        """Determine language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.vue': 'vue',
            '.html': 'html',
            '.css': 'css'
        }
        
        for ext, lang in ext_map.items():
            if file_path.endswith(ext):
                return lang
        
        return 'unknown'
    
    def _extract_metadata(self, file_path: str, code: str, framework: str) -> Dict:
        """Extract metadata from code"""
        metadata = {
            'file_path': file_path,
            'framework': framework,
            'lines_of_code': len(code.split('\n')),
            'has_tests': 'test' in file_path.lower(),
            'has_types': '.ts' in file_path or '.tsx' in file_path
        }
        
        # Extract imports
        if 'import' in code:
            imports = [line.strip() for line in code.split('\n') if line.strip().startswith('import')]
            metadata['imports'] = imports[:10]  # Limit to first 10
        
        return metadata
    
    def _categorize_code(self, file_path: str, code: str) -> str:
        """Categorize code by functionality"""
        path_lower = file_path.lower()
        code_lower = code.lower()
        
        categories = {
            'component': ['component', 'ui', 'widget'],
            'api': ['api', 'route', 'endpoint', 'controller'],
            'model': ['model', 'schema', 'entity'],
            'util': ['util', 'helper', 'tool'],
            'config': ['config', 'setting', 'env'],
            'test': ['test', 'spec', '__test__'],
            'hook': ['hook', 'use'],
            'middleware': ['middleware', 'interceptor'],
            'service': ['service', 'provider']
        }
        
        for category, keywords in categories.items():
            if any(keyword in path_lower or keyword in code_lower for keyword in keywords):
                return category
        
        return 'general'
    
    async def _save_template(
        self,
        file_path: str,
        code: str,
        framework: str,
        category: str,
        metadata: Dict,
        quality_score: float,
        source_url: str
    ):
        """Save template to database and vector store"""
        async with get_async_db() as db:
            # Create template record
            template = CodeTemplate(
                name=file_path.split('/')[-1],
                framework=framework,
                category=category,
                description=f"Template from {metadata.get('source_repo', 'unknown')}",
                code=code,
                metadata=metadata,
                quality_score=quality_score,
                source_url=source_url,
                validated=True
            )
            
            db.add(template)
            await db.commit()
            await db.refresh(template)
            
            # Add to vector store
            self.vector_store.add_template(
                template_id=template.id,
                code=code,
                metadata=metadata,
                description=template.description
            )
            
            logger.info(f"Saved template: {template.name}")
    
    async def search_and_add_repos(self, query: str, language: str, max_repos: int = 5):
        """Search for and add new repositories"""
        logger.info(f"Searching for {language} repositories with query: {query}")
        
        repos = self.github.search_repositories(
            query=query,
            language=language,
            stars_min=1000,
            max_results=max_repos
        )
        
        for repo_name in repos:
            try:
                await self.scrape_repository(repo_name, language)
            except Exception as e:
                logger.error(f"Error processing {repo_name}: {e}")


async def main():
    """Main function to run the scraper"""
    scraper = TemplateScraper()
    
    # Scrape approved repositories
    await scraper.scrape_all()
    
    # Optionally search for additional repositories
    # await scraper.search_and_add_repos("react components", "JavaScript", max_repos=3)
    # await scraper.search_and_add_repos("fastapi crud", "Python", max_repos=3)


if __name__ == "__main__":
    asyncio.run(main())
