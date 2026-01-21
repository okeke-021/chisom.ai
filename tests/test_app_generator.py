"""Tests for app generator agent"""
import pytest
from agents.app_generator_agent import AppGeneratorAgent, AppGeneratorState


class TestAppGeneratorAgent:
    """Test suite for AppGeneratorAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return AppGeneratorAgent()
    
    @pytest.mark.asyncio
    async def test_analyze_requirements(self, agent):
        """Test requirements analysis"""
        state = AppGeneratorState(
            user_description="Build a todo app with React",
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
        
        result = await agent._analyze_requirements(state)
        assert result["current_step"] == "Analyzing requirements..."
    
    @pytest.mark.asyncio
    async def test_select_tech_stack(self, agent):
        """Test tech stack selection"""
        state = AppGeneratorState(
            user_description="Build a blog with authentication",
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
        
        result = await agent._select_tech_stack(state)
        assert "tech_stack" in result
        assert len(result["tech_stack"]) > 0
    
    @pytest.mark.asyncio
    async def test_full_generation_workflow(self, agent):
        """Test complete app generation"""
        description = "Create a simple calculator app"
        
        result = await agent.generate_app(description)
        
        assert result["user_description"] == description
        assert "tech_stack" in result
        assert isinstance(result["errors"], list)
    
    def test_parse_tech_stack(self, agent):
        """Test tech stack parsing"""
        content = '{"framework": "React", "backend": "FastAPI"}'
        result = agent._parse_tech_stack(content)
        
        assert "framework" in result
        assert result["framework"] == "React"
    
    def test_categorize_code(self, agent):
        """Test code categorization"""
        # Test component categorization
        category = agent._categorize_code(
            "Button.component.jsx",
            "export const Button = () => {}"
        )
        assert category == "component"
        
        # Test API categorization
        category = agent._categorize_code(
            "api/users.py",
            "def get_users(): pass"
        )
        assert category == "api"


@pytest.mark.asyncio
async def test_state_persistence():
    """Test state persistence through workflow"""
    agent = AppGeneratorAgent()
    
    initial_state = AppGeneratorState(
        user_description="Test app",
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
    
    # Test that state is maintained through steps
    result = await agent._analyze_requirements(initial_state)
    assert result["user_description"] == "Test app"
