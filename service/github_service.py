"""GitHub integration service"""
from github import Github, GithubException
from typing import Dict, List, Optional
import base64
import logging
from config import settings

logger = logging.getLogger(__name__)


class GitHubService:
    """Handle GitHub operations"""
    
    def __init__(self):
        self.github = Github(settings.github_token)
        self.user = self.github.get_user()
    
    def create_repository(
        self, 
        repo_name: str, 
        description: str = "",
        private: bool = False
    ) -> str:
        """
        Create a new GitHub repository
        Returns: Repository URL
        """
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=True
            )
            logger.info(f"Created repository: {repo.html_url}")
            return repo.html_url
        except GithubException as e:
            logger.error(f"Error creating repository: {e}")
            raise
    
    def commit_files(
        self, 
        repo_name: str, 
        files: Dict[str, str],
        commit_message: str = "Initial commit"
    ) -> bool:
        """
        Commit multiple files to a repository
        files: Dict mapping file paths to content
        """
        try:
            repo = self.user.get_repo(repo_name)
            
            # Get the default branch
            default_branch = repo.default_branch
            branch = repo.get_branch(default_branch)
            
            # Create blobs for each file
            blobs = []
            for file_path, content in files.items():
                blob = repo.create_git_blob(content, "utf-8")
                blobs.append({
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob.sha
                })
            
            # Get base tree
            base_tree = repo.get_git_tree(branch.commit.sha)
            
            # Create new tree
            tree = repo.create_git_tree(blobs, base_tree)
            
            # Create commit
            parent = repo.get_git_commit(branch.commit.sha)
            commit = repo.create_git_commit(commit_message, tree, [parent])
            
            # Update reference
            ref = repo.get_git_ref(f"heads/{default_branch}")
            ref.edit(commit.sha)
            
            logger.info(f"Committed {len(files)} files to {repo_name}")
            return True
            
        except GithubException as e:
            logger.error(f"Error committing files: {e}")
            raise
    
    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> str:
        """Create a pull request"""
        try:
            repo = self.user.get_repo(repo_name)
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            logger.info(f"Created pull request: {pr.html_url}")
            return pr.html_url
        except GithubException as e:
            logger.error(f"Error creating pull request: {e}")
            raise
    
    def create_branch(self, repo_name: str, branch_name: str) -> bool:
        """Create a new branch"""
        try:
            repo = self.user.get_repo(repo_name)
            sb = repo.get_branch(repo.default_branch)
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=sb.commit.sha
            )
            logger.info(f"Created branch {branch_name} in {repo_name}")
            return True
        except GithubException as e:
            logger.error(f"Error creating branch: {e}")
            raise
    
    def scrape_repository_code(
        self, 
        repo_full_name: str,
        file_extensions: List[str] = [".py", ".js", ".jsx", ".ts", ".tsx", ".vue"]
    ) -> Dict[str, str]:
        """
        Scrape code files from a repository
        Returns: Dict mapping file paths to content
        """
        try:
            repo = self.github.get_repo(repo_full_name)
            contents = repo.get_contents("")
            code_files = {}
            
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    # Check if file has relevant extension
                    if any(file_content.path.endswith(ext) for ext in file_extensions):
                        try:
                            content = base64.b64decode(file_content.content).decode('utf-8')
                            code_files[file_content.path] = content
                        except Exception as e:
                            logger.warning(f"Error decoding {file_content.path}: {e}")
            
            logger.info(f"Scraped {len(code_files)} files from {repo_full_name}")
            return code_files
            
        except GithubException as e:
            logger.error(f"Error scraping repository: {e}")
            raise
    
    def search_repositories(
        self,
        query: str,
        language: Optional[str] = None,
        stars_min: int = 100,
        max_results: int = 10
    ) -> List[str]:
        """
        Search for repositories
        Returns: List of repository full names
        """
        try:
            query_str = f"{query} stars:>={stars_min}"
            if language:
                query_str += f" language:{language}"
            
            repositories = self.github.search_repositories(query=query_str)
            
            repo_names = []
            for i, repo in enumerate(repositories):
                if i >= max_results:
                    break
                repo_names.append(repo.full_name)
            
            logger.info(f"Found {len(repo_names)} repositories for query: {query}")
            return repo_names
            
        except GithubException as e:
            logger.error(f"Error searching repositories: {e}")
            raise
