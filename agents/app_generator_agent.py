"""LangGraph agent for web app generation"""
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import Graph, StateGraph, END
from langchain_mistralai import ChatMistralAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import operator
import logging
from config import settings

logger = logging.getLogger(__name__)


class AppGeneratorState(TypedDict):
    """State for the app generator workflow"""
    user_description: str
    tech_stack: Dict[str, str]
    project_structure: Dict[str, str]
    generated_files: Dict[str, str]
    dockerfile: str
    docker_compose: str
    readme: str
    github_repo_url: str
    errors: Annotated[List[str], operator.add]
    current_step: str


class AppGeneratorAgent:
    """Agent for generating complete web applications"""
    
    def __init__(self):
        self.llm = ChatMistralAI(
            model="codestral-latest",
            mistral_api_key=settings.mistral_api_key,
            temperature=0.2
        )
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> Graph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AppGeneratorState)
        
        # Add nodes
        workflow.add_node("analyze_requirements", self._analyze_requirements)
        workflow.add_node("select_tech_stack", self._select_tech_stack)
        workflow.add_node("design_architecture", self._design_architecture)
        workflow.add_node("generate_backend", self._generate_backend)
        workflow.add_node("generate_frontend", self._generate_frontend)
        workflow.add_node("generate_docker", self._generate_docker)
        workflow.add_node("generate_documentation", self._generate_documentation)
        
        # Define edges
        workflow.set_entry_point("analyze_requirements")
        workflow.add_edge("analyze_requirements", "select_tech_stack")
        workflow.add_edge("select_tech_stack", "design_architecture")
        workflow.add_edge("design_architecture", "generate_backend")
        workflow.add_edge("generate_backend", "generate_frontend")
        workflow.add_edge("generate_frontend", "generate_docker")
        workflow.add_edge("generate_docker", "generate_documentation")
        workflow.add_edge("generate_documentation", END)
        
        return workflow.compile()
    
    async def _analyze_requirements(self, state: AppGeneratorState) -> AppGeneratorState:
        """Analyze user requirements"""
        logger.info("Analyzing requirements")
        state["current_step"] = "Analyzing requirements..."
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert software architect. Analyze the user's 
            description and extract key requirements, features, and technical needs."""),
            HumanMessage(content=f"User wants to build: {state['user_description']}\n\n"
                        "Extract and list the main features and requirements.")
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            logger.info(f"Requirements analyzed: {response.content}")
        except Exception as e:
            logger.error(f"Error analyzing requirements: {e}")
            state["errors"].append(f"Requirements analysis error: {str(e)}")
        
        return state
    
    async def _select_tech_stack(self, state: AppGeneratorState) -> AppGeneratorState:
        """Select appropriate tech stack"""
        logger.info("Selecting tech stack")
        state["current_step"] = "Selecting optimal tech stack..."
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a tech stack expert. Based on the requirements,
            recommend the best technology stack. Consider: framework, database, styling, 
            state management, authentication, etc. Return as JSON."""),
            HumanMessage(content=f"Requirements: {state['user_description']}\n\n"
                        "Provide tech stack in JSON format with keys: framework, database, "
                        "styling, backend, features")
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            # Parse and store tech stack
            tech_stack = self._parse_tech_stack(response.content)
            state["tech_stack"] = tech_stack
            logger.info(f"Tech stack selected: {tech_stack}")
        except Exception as e:
            logger.error(f"Error selecting tech stack: {e}")
            state["errors"].append(f"Tech stack selection error: {str(e)}")
        
        return state
    
    async def _design_architecture(self, state: AppGeneratorState) -> AppGeneratorState:
        """Design project architecture"""
        logger.info("Designing architecture")
        state["current_step"] = "Designing project architecture..."
        
        tech_stack_str = str(state.get("tech_stack", {}))
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a software architect. Design the project 
            structure including folder hierarchy and file organization. Return as JSON 
            with file paths as keys and brief descriptions as values."""),
            HumanMessage(content=f"Tech stack: {tech_stack_str}\n"
                        f"Requirements: {state['user_description']}\n\n"
                        "Design the project structure.")
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            structure = self._parse_project_structure(response.content)
            state["project_structure"] = structure
            logger.info(f"Architecture designed with {len(structure)} components")
        except Exception as e:
            logger.error(f"Error designing architecture: {e}")
            state["errors"].append(f"Architecture design error: {str(e)}")
        
        return state
    
    async def _generate_backend(self, state: AppGeneratorState) -> AppGeneratorState:
        """Generate backend code"""
        logger.info("Generating backend code")
        state["current_step"] = "Generating backend code..."
        
        tech_stack = state.get("tech_stack", {})
        backend_framework = tech_stack.get("backend", "FastAPI")
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are an expert {backend_framework} developer. 
            Generate production-ready backend code with proper structure, error handling,
            and best practices."""),
            HumanMessage(content=f"Requirements: {state['user_description']}\n"
                        f"Tech stack: {tech_stack}\n\n"
                        "Generate complete backend code. Include main app file, routes, models, "
                        "and configuration.")
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            backend_files = self._extract_code_files(response.content, "backend")
            state["generated_files"].update(backend_files)
            logger.info(f"Generated {len(backend_files)} backend files")
        except Exception as e:
            logger.error(f"Error generating backend: {e}")
            state["errors"].append(f"Backend generation error: {str(e)}")
        
        return state
    
    async def _generate_frontend(self, state: AppGeneratorState) -> AppGeneratorState:
        """Generate frontend code"""
        logger.info("Generating frontend code")
        state["current_step"] = "Generating frontend code..."
        
        tech_stack = state.get("tech_stack", {})
        frontend_framework = tech_stack.get("framework", "React")
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are an expert {frontend_framework} developer. 
            Generate production-ready frontend code with modern best practices, 
            responsive design, and clean architecture."""),
            HumanMessage(content=f"Requirements: {state['user_description']}\n"
                        f"Tech stack: {tech_stack}\n\n"
                        "Generate complete frontend code including components, pages, "
                        "and styling.")
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            frontend_files = self._extract_code_files(response.content, "frontend")
            state["generated_files"].update(frontend_files)
            logger.info(f"Generated {len(frontend_files)} frontend files")
        except Exception as e:
            logger.error(f"Error generating frontend: {e}")
            state["errors"].append(f"Frontend generation error: {str(e)}")
        
        return state
    
    async def _generate_docker(self, state: AppGeneratorState) -> AppGeneratorState:
        """Generate Docker configuration"""
        logger.info("Generating Docker configuration")
        state["current_step"] = "Generating Docker configuration..."
        
        tech_stack = state.get("tech_stack", {})
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a DevOps expert. Generate production-ready 
            Dockerfile and docker-compose.yml for the application."""),
            HumanMessage(content=f"Tech stack: {tech_stack}\n\n"
                        "Generate Dockerfile and docker-compose.yml")
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            docker_files = self._extract_docker_files(response.content)
            state.update(docker_files)
            logger.info("Docker configuration generated")
        except Exception as e:
            logger.error(f"Error generating Docker config: {e}")
            state["errors"].append(f"Docker generation error: {str(e)}")
        
        return state
    
    async def _generate_documentation(self, state: AppGeneratorState) -> AppGeneratorState:
        """Generate documentation"""
        logger.info("Generating documentation")
        state["current_step"] = "Generating documentation..."
        
        tech_stack = state.get("tech_stack", {})
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a technical writer. Generate comprehensive 
            README.md with setup instructions, features, and usage guide."""),
            HumanMessage(content=f"Project: {state['user_description']}\n"
                        f"Tech stack: {tech_stack}\n\n"
                        "Generate detailed README.md")
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            state["readme"] = response.content
            logger.info("Documentation generated")
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            state["errors"].append(f"Documentation generation error: {str(e)}")
        
        return state
    
    def _parse_tech_stack(self, content: str) -> Dict[str, str]:
        """Parse tech stack from LLM response"""
        # Implement JSON extraction logic
        import json
        import re
        
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return {
            "framework": "React",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "styling": "Tailwind CSS"
        }
    
    def _parse_project_structure(self, content: str) -> Dict[str, str]:
        """Parse project structure from LLM response"""
        # Simplified parser
        return {
            "src/": "Source code directory",
            "public/": "Public assets",
            "tests/": "Test files"
        }
    
    def _extract_code_files(self, content: str, prefix: str) -> Dict[str, str]:
        """Extract code files from LLM response"""
        # Implement code block extraction
        files = {}
        # Simplified extraction
        return files
    
    def _extract_docker_files(self, content: str) -> Dict[str, str]:
        """Extract Docker files from LLM response"""
        return {
            "dockerfile": "# Dockerfile content",
            "docker_compose": "# docker-compose.yml content"
        }
    
    async def generate_app(self, description: str) -> AppGeneratorState:
        """Main method to generate complete app"""
        initial_state = AppGeneratorState(
            user_description=description,
            tech_stack={},
            project_structure={},
            generated_files={},
            dockerfile="",
            docker_compose="",
            readme="",
            github_repo_url="",
            errors=[],
            current_step=""
        )
        
        final_state = await self.workflow.ainvoke(initial_state)
        return final_state
