"""Code quality analysis and filtering service"""
import subprocess
import tempfile
import os
import json
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class CodeQualityService:
    """Analyze code quality using ESLint and Prettier"""
    
    @staticmethod
    def analyze_javascript(code: str) -> Tuple[bool, List[str], float]:
        """
        Analyze JavaScript/TypeScript code quality
        Returns: (is_valid, issues, quality_score)
        """
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.js', 
            delete=False
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        
        try:
            # Run ESLint
            eslint_result = subprocess.run(
                ['npx', 'eslint', '--format', 'json', tmp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            issues = []
            quality_score = 100.0
            
            if eslint_result.stdout:
                try:
                    eslint_output = json.loads(eslint_result.stdout)
                    if eslint_output and len(eslint_output) > 0:
                        messages = eslint_output[0].get('messages', [])
                        issues = [msg['message'] for msg in messages]
                        
                        # Calculate quality score
                        error_count = sum(1 for msg in messages if msg['severity'] == 2)
                        warning_count = sum(1 for msg in messages if msg['severity'] == 1)
                        quality_score = max(0, 100 - (error_count * 10) - (warning_count * 5))
                except json.JSONDecodeError:
                    logger.warning("Could not parse ESLint output")
            
            is_valid = quality_score >= 70
            return is_valid, issues, quality_score
            
        except subprocess.TimeoutExpired:
            logger.warning("ESLint analysis timed out")
            return False, ["Analysis timeout"], 0.0
        except FileNotFoundError:
            logger.warning("ESLint not installed, skipping analysis")
            return True, [], 80.0
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @staticmethod
    def analyze_python(code: str) -> Tuple[bool, List[str], float]:
        """
        Analyze Python code quality
        Returns: (is_valid, issues, quality_score)
        """
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.py', 
            delete=False
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        
        try:
            # Run Ruff
            ruff_result = subprocess.run(
                ['ruff', 'check', '--output-format', 'json', tmp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            issues = []
            quality_score = 100.0
            
            if ruff_result.stdout:
                try:
                    ruff_output = json.loads(ruff_result.stdout)
                    issues = [item['message'] for item in ruff_output]
                    
                    # Calculate quality score
                    quality_score = max(0, 100 - (len(issues) * 5))
                except json.JSONDecodeError:
                    logger.warning("Could not parse Ruff output")
            
            is_valid = quality_score >= 70
            return is_valid, issues, quality_score
            
        except subprocess.TimeoutExpired:
            logger.warning("Ruff analysis timed out")
            return False, ["Analysis timeout"], 0.0
        except FileNotFoundError:
            logger.warning("Ruff not installed, skipping analysis")
            return True, [], 80.0
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @staticmethod
    def format_code(code: str, language: str) -> str:
        """Format code using appropriate formatter"""
        if language in ['javascript', 'typescript', 'jsx', 'tsx']:
            return CodeQualityService._format_with_prettier(code)
        elif language == 'python':
            return CodeQualityService._format_with_black(code)
        return code
    
    @staticmethod
    def _format_with_prettier(code: str) -> str:
        """Format JavaScript/TypeScript with Prettier"""
        try:
            result = subprocess.run(
                ['npx', 'prettier', '--parser', 'babel'],
                input=code,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout if result.returncode == 0 else code
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return code
    
    @staticmethod
    def _format_with_black(code: str) -> str:
        """Format Python with Black"""
        try:
            result = subprocess.run(
                ['black', '-', '--quiet'],
                input=code,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout if result.returncode == 0 else code
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return code
    
    @staticmethod
    def validate_syntax(code: str, language: str) -> Tuple[bool, str]:
        """
        Validate code syntax
        Returns: (is_valid, error_message)
        """
        if language == 'python':
            try:
                compile(code, '<string>', 'exec')
                return True, ""
            except SyntaxError as e:
                return False, str(e)
        
        elif language in ['javascript', 'typescript']:
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.js', 
                delete=False
            ) as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            
            try:
                result = subprocess.run(
                    ['node', '--check', tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                is_valid = result.returncode == 0
                error_msg = result.stderr if not is_valid else ""
                return is_valid, error_msg
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return True, ""  # Assume valid if can't check
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        return True, ""  # Default to valid for unknown languages
