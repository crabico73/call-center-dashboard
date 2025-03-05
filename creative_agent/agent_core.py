"""
Core implementation of the Creative Agent
"""

import json
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Resources:
    """Track Hope's resources and tools"""
    computer_specs: Dict = None
    internet_specs: Dict = None
    available_tools: Dict = None
    
    def __post_init__(self):
        self.computer_specs = {
            "type": "Mid-range laptop",
            "initial_cost": 1000.00
        }
        
        self.internet_specs = {
            "type": "Home broadband",
            "monthly_cost": 50.00
        }
        
        self.available_tools = {
            "Canva": 0.00,        # Free tier for design
            "WordPress": 0.00,     # Free for blogging
            "GitHub": 0.00,       # Free for coding
            "Grammarly": 0.00,    # Free tier for writing
            "OBS Studio": 0.00,   # Free for video recording
        }

class CreativeAgent:
    """Core agent implementation for Hope AI"""
    
    def __init__(self, name: str, career_stage: str, work_hours: int, initial_skills: Dict[str, float]):
        self.name = name
        self.career_stage = career_stage.lower()
        self.max_hours_per_day = work_hours
        self.skills = initial_skills
        
        # Initialize state
        self.earnings = 0.0
        self.creator_share = 0.25
        self.hours_worked_today = 0
        self.jobs_completed = 0
        self.strategy = "skill building"
        self.patience = 100
        self.motivation = 100
        
        # Initialize resources and tracking
        self.resources = Resources()
        self.portfolio = []
        self.client_feedback = []
        self.successful_strategies = {}
        self.failed_strategies = {}
        self.production_company = None
        
        # Load previous state if exists
        self.load_state()
    
    def load_state(self):
        """Load agent state from disk"""
        if os.path.exists("state.json"):
            with open("state.json", "r") as f:
                state = json.load(f)
                self.__dict__.update(state)
    
    def save_state(self):
        """Save agent state to disk"""
        state = {
            "earnings": self.earnings,
            "jobs_completed": self.jobs_completed,
            "strategy": self.strategy,
            "skills": self.skills,
            "portfolio": self.portfolio,
            "client_feedback": self.client_feedback,
            "creator_share": self.creator_share,
            "hours_worked_today": self.hours_worked_today,
            "career_stage": self.career_stage,
            "production_company": self.production_company,
            "successful_strategies": self.successful_strategies,
            "failed_strategies": self.failed_strategies
        }
        
        with open("state.json", "w") as f:
            json.dump(state, f, indent=2)
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "name": self.name,
            "earnings": self.earnings,
            "jobs_completed": self.jobs_completed,
            "current_strategy": self.strategy,
            "patience_level": self.patience,
            "motivation_level": self.motivation,
            "skills": self.skills,
            "portfolio_size": len(self.portfolio),
            "career_stage": self.career_stage,
            "hours_worked_today": self.hours_worked_today,
            "max_hours_per_day": self.max_hours_per_day,
            "production_company": self.production_company
        }
    
    def improve_skill(self, skill: str, hours: float = 1.0) -> bool:
        """Improve a specific skill through practice"""
        if skill in self.skills:
            improvement = hours * 0.01 * (1 + random.random() * 0.5)
            self.skills[skill] += improvement
            return True
        return False
    
    def check_career_progression(self):
        """Check and update career stage based on progress"""
        if self.career_stage == "beginner" and self.jobs_completed >= 20:
            self.career_stage = "indie"
            return True
            
        elif self.career_stage == "indie" and self.earnings > 5000:
            self.career_stage = "professional"
            return True
            
        elif self.career_stage == "professional" and self.earnings > 20000:
            self.career_stage = "producer"
            self.production_company = {
                "name": f"{self.name} Productions",
                "founded": time.strftime("%Y-%m-%d"),
                "projects": []
            }
            return True
            
        return False
    
    def take_action(self) -> Optional[Dict]:
        """Take a career action and return the results"""
        if self.hours_worked_today >= self.max_hours_per_day:
            return None
            
        # Simulate action results
        hours_spent = random.randint(1, 4)
        if self.hours_worked_today + hours_spent > self.max_hours_per_day:
            hours_spent = self.max_hours_per_day - self.hours_worked_today
            
        self.hours_worked_today += hours_spent
        
        # Calculate success chance based on skills and strategy
        avg_skill = sum(self.skills.values()) / len(self.skills)
        success_chance = min(0.7 + (avg_skill * 0.1), 0.9)
        
        if random.random() < success_chance:
            earnings = random.randint(50, 200) * (1 + (avg_skill - 1) * 0.5)
            self.earnings += earnings
            self.jobs_completed += 1
            
            return {
                "success": True,
                "hours_spent": hours_spent,
                "earnings": earnings,
                "skills_improved": [
                    skill for skill in self.skills.keys()
                    if self.improve_skill(skill, hours_spent * 0.2)
                ]
            }
        
        # Learning from failure
        for skill in self.skills:
            self.improve_skill(skill, hours_spent * 0.1)
            
        return {
            "success": False,
            "hours_spent": hours_spent,
            "earnings": 0,
            "skills_improved": list(self.skills.keys())
        } 