from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from datetime import datetime

@dataclass
class Resources:
    """Track available resources and their costs"""
    computer_specs = {
        "cpu": "AMD Ryzen 9 7950X / Intel i9-13900K",
        "gpu": "NVIDIA RTX 4080",
        "ram": "64GB DDR5",
        "storage": "4TB NVMe SSD",
        "initial_cost": 3000.00
    }
    
    internet_specs = {
        "download": "1 Gbps",
        "upload": "500 Mbps",
        "monthly_cost": 80.00
    }
    
    current_balance: float = 5000.00  # Starting budget including computer cost
    monthly_expenses: float = 80.00   # Internet cost
    available_tools: Dict[str, float] = None  # Tools and their costs
    
    def __post_init__(self):
        self.available_tools = {
            "Blender": 0.00,  # Free, professional 3D creation suite
            "DaVinci Resolve": 0.00,  # Free version for video editing
            "GIMP": 0.00,  # Free image editing
            "Audacity": 0.00,  # Free audio editing
            "OBS Studio": 0.00,  # Free recording/streaming
            "Python": 0.00,  # Free programming language
            "Git": 0.00,  # Free version control
        }
        self.current_balance -= self.computer_specs["initial_cost"]

class CreativeAgent:
    def __init__(self):
        self.resources = Resources()
        self.project_history = []
        self.current_project = None
        self.skills = {
            "3D_Modeling": 1,
            "Animation": 1,
            "Video_Editing": 1,
            "Scripting": 1,
            "Sound_Design": 1,
            "Project_Management": 1
        }
        self.revenue = 0.0
        self.goals = {
            "short_term": [
                "Master basic 3D modeling in Blender",
                "Create first short animation",
                "Build social media presence",
                "Generate first revenue stream"
            ],
            "medium_term": [
                "Develop unique animation style",
                "Build subscriber base",
                "Create consistent revenue stream",
                "Expand tool capabilities"
            ],
            "long_term": [
                "Compete with studio-quality productions",
                "Build sustainable animation business",
                "Create original IP franchise",
                "Scale operations with AI integration"
            ]
        }

    def analyze_market_opportunity(self, content_type: str) -> Dict:
        """Analyze current market opportunities for specific content types"""
        opportunities = {
            "animation": {
                "platforms": ["YouTube", "TikTok", "Netflix Independent", "Vimeo"],
                "trending_genres": ["Educational", "Sci-Fi", "Fantasy", "Slice of Life"],
                "monetization": ["Ad Revenue", "Patreon", "Merchandise", "Licensing"],
                "entry_barriers": "Low - Free tools available",
                "competition_level": "Medium - Quality matters more than budget",
                "growth_potential": "High - Multiple revenue streams possible"
            }
        }
        return opportunities.get(content_type, {})

    def plan_project(self, project_type: str, duration_days: int) -> Dict:
        """Create a project plan with timeline and resource allocation"""
        return {
            "type": project_type,
            "duration": duration_days,
            "required_tools": self.resources.available_tools,
            "estimated_costs": self._calculate_project_costs(duration_days),
            "potential_revenue": self._estimate_revenue(project_type),
            "skill_requirements": self._get_required_skills(project_type),
            "timeline": self._create_timeline(duration_days)
        }

    def _calculate_project_costs(self, duration_days: int) -> float:
        """Calculate project costs including utilities and tools"""
        monthly_costs = self.resources.monthly_expenses
        daily_cost = monthly_costs / 30
        return daily_cost * duration_days

    def _estimate_revenue(self, project_type: str) -> Dict:
        """Estimate potential revenue streams for the project"""
        return {
            "ad_revenue": "Estimated $1-5 per 1000 views",
            "patreon": "Potential $1-10 per patron per month",
            "merchandise": "20-40% margin on print-on-demand items",
            "licensing": "Variable based on usage rights"
        }

    def _get_required_skills(self, project_type: str) -> Dict:
        """Determine required skills and current skill gaps"""
        return {skill: level for skill, level in self.skills.items()}

    def _create_timeline(self, duration_days: int) -> List[Dict]:
        """Create a project timeline with milestones"""
        return [
            {"phase": "Pre-production", "days": duration_days * 0.2},
            {"phase": "Production", "days": duration_days * 0.6},
            {"phase": "Post-production", "days": duration_days * 0.2}
        ]

    def improve_skill(self, skill_name: str, hours_practiced: int):
        """Improve a specific skill based on practice hours"""
        if skill_name in self.skills:
            self.skills[skill_name] += hours_practiced * 0.01
            return f"Improved {skill_name} to level {self.skills[skill_name]:.2f}"
        return "Skill not found"

    def get_next_steps(self) -> List[str]:
        """Get recommended next steps based on current state"""
        return [
            "Complete Blender Fundamentals course (free on Blender.org)",
            "Create a 30-second animation test",
            "Set up YouTube and social media channels",
            "Join online animation communities for feedback",
            "Start building portfolio with small projects"
        ]

    def generate_report(self) -> Dict:
        """Generate a status report of current progress"""
        return {
            "current_balance": self.resources.current_balance,
            "monthly_expenses": self.resources.monthly_expenses,
            "skills": self.skills,
            "revenue": self.revenue,
            "available_tools": self.resources.available_tools,
            "next_steps": self.get_next_steps()
        } 