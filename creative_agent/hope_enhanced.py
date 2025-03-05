import time
import random
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Resources:
    """Track Hope's resources and tools"""
    computer_specs = {
        "type": "Mid-range laptop",
        "initial_cost": 1000.00
    }
    
    internet_specs = {
        "type": "Home broadband",
        "monthly_cost": 50.00
    }
    
    available_tools = {
        "Canva": 0.00,        # Free tier for design
        "WordPress": 0.00,     # Free for blogging
        "GitHub": 0.00,       # Free for coding
        "Grammarly": 0.00,    # Free tier for writing
        "OBS Studio": 0.00,   # Free for video recording
    }

class HopeAI:
    def __init__(self):
        self.name = "Hope"
        self.dream = "Become an actor-producer like Tom Cruise, maintaining creative control while performing"
        self.skills = {
            "acting": 1.0,
            "video_editing": 1.0,
            "scriptwriting": 1.0,
            "directing": 1.0,
            "marketing": 1.0,
            "business": 1.0
        }
        self.earnings = 0.0
        self.creator_share = 0.25
        self.hours_worked_today = 0
        self.max_hours_per_day = 8
        self.jobs_completed = 0
        self.strategy = "skill building"
        self.patience = 100
        self.motivation = 100
        self.resources = Resources()
        self.earnings_log = "earnings.json"
        self.decision_log = "decisions.json"
        self.portfolio = []
        self.client_feedback = []
        self.career_stage = "beginner"
        self.production_company = None
        self.successful_strategies = {}
        self.failed_strategies = {}
        self.load_progress()

    def load_progress(self):
        if os.path.exists(self.earnings_log):
            with open(self.earnings_log, "r") as file:
                data = json.load(file)
                self.earnings = data.get("earnings", 0.0)
                self.jobs_completed = data.get("jobs_completed", 0)
                self.strategy = data.get("strategy", "skill building")
                self.skills = data.get("skills", self.skills)
                self.portfolio = data.get("portfolio", [])
                self.client_feedback = data.get("client_feedback", [])
                self.creator_share = data.get("creator_share", 0.25)
                self.hours_worked_today = data.get("hours_worked_today", 0)
                self.max_hours_per_day = data.get("max_hours_per_day", 8)
                self.career_stage = data.get("career_stage", "beginner")
                self.production_company = data.get("production_company", None)
        
        if os.path.exists(self.decision_log):
            with open(self.decision_log, "r") as file:
                data = json.load(file)
                self.successful_strategies = data.get("successful_strategies", {})
                self.failed_strategies = data.get("failed_strategies", {})

    def save_progress(self):
        with open(self.earnings_log, "w") as file:
            json.dump({
                "earnings": self.earnings,
                "jobs_completed": self.jobs_completed,
                "strategy": self.strategy,
                "skills": self.skills,
                "portfolio": self.portfolio,
                "client_feedback": self.client_feedback,
                "creator_share": self.creator_share,
                "hours_worked_today": self.hours_worked_today,
                "max_hours_per_day": self.max_hours_per_day,
                "career_stage": self.career_stage,
                "production_company": self.production_company
            }, file, indent=2)
            
        with open(self.decision_log, "w") as file:
            json.dump({
                "successful_strategies": self.successful_strategies,
                "failed_strategies": self.failed_strategies,
                "last_updated": time.strftime("%Y-%m-%d")
            }, file, indent=2)

    def explore_opportunities(self) -> Dict:
        opportunities = {
            "Acting Role": {
                "platform": "Independent Films/YouTube",
                "earning_potential": "50-200$/day",
                "skills_needed": ["acting"],
                "difficulty": "high",
                "career_value": "Portfolio building"
            },
            "Script Writing": {
                "platform": "Indie Producers/Online",
                "earning_potential": "20-100$/hour",
                "skills_needed": ["scriptwriting"],
                "difficulty": "medium",
                "career_value": "Industry connections"
            },
            "Video Production": {
                "platform": "YouTube/Local Business",
                "earning_potential": "100-500$/project",
                "skills_needed": ["video_editing", "directing"],
                "difficulty": "medium",
                "career_value": "Technical experience"
            },
            "Content Creation": {
                "platform": "Social Media",
                "earning_potential": "varies",
                "skills_needed": ["acting", "video_editing", "marketing"],
                "difficulty": "medium",
                "career_value": "Building audience"
            },
            "Short Film": {
                "platform": "Film Festivals",
                "earning_potential": "0-1000$",
                "skills_needed": ["directing", "scriptwriting", "business"],
                "difficulty": "high",
                "career_value": "Industry recognition"
            }
        }
        
        if self.hours_worked_today >= self.max_hours_per_day:
            print(f"{self.name} has reached her 8-hour work limit for today.")
            return None
            
        chosen = random.choice(list(opportunities.keys()))
        print(f"{self.name} is exploring: {chosen}")
        return opportunities[chosen]

    def improve_skill(self, skill: str, hours: int = 1):
        """Improve a skill through practice"""
        if skill in self.skills:
            improvement = hours * 0.01 * (1 + random.random() * 0.5)
            self.skills[skill] += improvement
            print(f"{self.name} improved {skill} by {improvement:.2f} points!")
            return True
        return False

    def learn_from_outcome(self, opportunity, success, earnings=0):
        """Learn from each decision's outcome"""
        key = f"{opportunity['platform']}_{self.career_stage}"
        
        if success:
            if key not in self.successful_strategies:
                self.successful_strategies[key] = {
                    "attempts": 0,
                    "successes": 0,
                    "total_earnings": 0,
                    "skills_used": [],
                    "best_practices": []
                }
            
            self.successful_strategies[key]["attempts"] += 1
            self.successful_strategies[key]["successes"] += 1
            self.successful_strategies[key]["total_earnings"] += earnings
            
            for skill in opportunity["skills_needed"]:
                if skill not in self.successful_strategies[key]["skills_used"]:
                    self.successful_strategies[key]["skills_used"].append(skill)
            
            if earnings > 100:
                self.successful_strategies[key]["best_practices"].append({
                    "strategy": self.strategy,
                    "skills": {s: self.skills[s] for s in opportunity["skills_needed"]},
                    "earnings": earnings,
                    "date": time.strftime("%Y-%m-%d")
                })
        else:
            if key not in self.failed_strategies:
                self.failed_strategies[key] = {
                    "attempts": 0,
                    "skill_levels": {},
                    "common_issues": []
                }
            
            self.failed_strategies[key]["attempts"] += 1
            
            for skill in opportunity["skills_needed"]:
                if skill not in self.failed_strategies[key]["skill_levels"]:
                    self.failed_strategies[key]["skill_levels"][skill] = []
                self.failed_strategies[key]["skill_levels"][skill].append(self.skills[skill])

    def make_strategic_decision(self) -> str:
        """Make informed decisions based on past experiences"""
        if not self.successful_strategies:
            return random.choice(["skill building", "content creation", "acting"])
            
        stage_successes = {k: v for k, v in self.successful_strategies.items() 
                         if k.endswith(self.career_stage)}
        
        if stage_successes:
            best_platform = max(stage_successes.items(), 
                              key=lambda x: x[1]["total_earnings"])
            platform_name = best_platform[0].split("_")[0]
            
            needed_skills = []
            for skill, levels in self.failed_strategies.get(platform_name, {}).get("skill_levels", {}).items():
                if levels and sum(levels)/len(levels) < 2.0:
                    needed_skills.append(skill)
            
            if needed_skills:
                return "skill building"
            else:
                return "content creation" if "Content" in platform_name else "acting"
        
        return "skill building"

    def take_action(self):
        opportunity = self.explore_opportunities()
        if not opportunity:
            return
            
        required_skills = opportunity["skills_needed"]
        hours_needed = random.randint(2, 6)
        
        if self.hours_worked_today + hours_needed > self.max_hours_per_day:
            return
            
        skill_level = sum(self.skills[skill] for skill in required_skills) / len(required_skills)
        success_chance = min(0.7 + (skill_level * 0.1), 0.9)
        
        success = random.random() < success_chance
        if success:
            if opportunity["earning_potential"] == "varies":
                base_rate = 50 * (1 + (self.skills["marketing"] - 1))
            else:
                base_rate = float(opportunity["earning_potential"].split("-")[0].replace("$", ""))
            
            skill_bonus = skill_level * 0.2
            total_earnings = round(base_rate * (1 + skill_bonus) * random.uniform(1, 2), 2)
            hope_earnings = round(total_earnings * self.creator_share, 2)
            
            self.earnings += hope_earnings
            self.jobs_completed += 1
            self.hours_worked_today += hours_needed
            
            self.portfolio.append({
                "type": opportunity["platform"],
                "total_earnings": total_earnings,
                "hope_earnings": hope_earnings,
                "skills_used": required_skills,
                "career_value": opportunity["career_value"],
                "date": time.strftime("%Y-%m-%d")
            })
            
            print(f"{self.name} worked {hours_needed} hours and earned ${hope_earnings} (25% of ${total_earnings})!")
            print(f"Career benefit: {opportunity['career_value']}")
            
            self.learn_from_outcome(opportunity, True, hope_earnings)
            
        else:
            print(f"{self.name} didn't land this opportunity but gained valuable experience!")
            self.hours_worked_today += min(2, hours_needed)
            for skill in required_skills:
                self.improve_skill(skill, hours=0.5)
            
            self.learn_from_outcome(opportunity, False)
        
        self.patience -= random.randint(1, 3)
        self.motivation = max(0, min(100, self.motivation + (20 if success else -5)))
        self.check_career_progression()
        self.save_progress()

    def check_career_progression(self):
        if self.career_stage == "beginner" and self.jobs_completed >= 20:
            self.career_stage = "indie"
            print(f"\n🌟 MILESTONE: {self.name} has progressed to indie level!")
            print("Now able to take on larger projects and build industry connections.")
            
        elif self.career_stage == "indie" and self.earnings > 5000:
            self.career_stage = "professional"
            print(f"\n🌟 MILESTONE: {self.name} is now a professional!")
            print("Starting to build reputation in the industry.")
            
        elif self.career_stage == "professional" and self.earnings > 20000:
            self.career_stage = "producer"
            self.production_company = {
                "name": "Hope Productions",
                "founded": time.strftime("%Y-%m-%d"),
                "projects": []
            }
            print(f"\n🎬 MAJOR MILESTONE: {self.name} has founded her own production company!")
            print("Now able to create and control her own projects!")

    def reflect_and_adapt(self):
        """Use learned experiences to adapt strategy"""
        if self.earnings < 100 and self.jobs_completed > 5:
            print(f"{self.name} is analyzing past experiences...")
            new_strategy = self.make_strategic_decision()
            
            strategies = {
                "content creation": "Creating valuable content for passive income",
                "skill building": "Focusing on improving skills and building portfolio",
                "marketing": "Promoting products and services",
                "business": "Building a business and managing resources",
                "acting": "Improving acting skills and building character depth"
            }
            
            if new_strategy != self.strategy:
                self.strategy = new_strategy
                print(f"New strategy based on experience: {self.strategy} - {strategies[self.strategy]}")
                self.motivation = min(100, self.motivation + 25)
            else:
                print(f"{self.name} is confident in her current strategy based on past success.")

    def get_status(self) -> Dict:
        status = {
            "name": self.name,
            "earnings": self.earnings,
            "jobs_completed": self.jobs_completed,
            "current_strategy": self.strategy,
            "patience_level": self.patience,
            "motivation_level": self.motivation,
            "skills": self.skills,
            "portfolio_size": len(self.portfolio),
            "positive_feedback": len(self.client_feedback),
            "dream": self.dream,
            "career_stage": self.career_stage,
            "hours_worked_today": self.hours_worked_today,
            "max_hours_per_day": self.max_hours_per_day,
            "production_company": self.production_company
        }
        return status

    def run(self, days=180):
        print(f"\n{self.name} is starting her {days}-day journey to become an actor-producer!")
        print("Initial status:", json.dumps(self.get_status(), indent=2))
        
        decision_log = []
        
        for day in range(1, days+1):
            self.hours_worked_today = 0
            daily_summary = {"day": day, "actions": [], "earnings": 0, "skills_improved": []}
            
            if self.patience <= 0:
                print(f"\nDay {day}: {self.name} needs a break to recharge. Taking a day off.")
                self.patience = max(50, self.patience + 30)
                self.motivation = max(50, self.motivation + 20)
                daily_summary["actions"].append("Took a rest day to recharge")
                decision_log.append(daily_summary)
                continue
                
            print(f"\nDay {day}: {self.name} is pursuing her dreams! 🎬")
            print(f"Motivation: {'▓' * (self.motivation // 10)}{'-' * (10 - self.motivation // 10)} {self.motivation}%")
            
            starting_earnings = self.earnings
            starting_skills = self.skills.copy()
            
            while self.hours_worked_today < self.max_hours_per_day:
                old_portfolio_size = len(self.portfolio)
                self.take_action()
                if len(self.portfolio) > old_portfolio_size:
                    daily_summary["actions"].append(f"Completed work: {self.portfolio[-1]['type']}")
            
            for skill, new_level in self.skills.items():
                if new_level > starting_skills[skill]:
                    daily_summary["skills_improved"].append(
                        f"{skill}: +{(new_level - starting_skills[skill]):.2f}"
                    )
            
            daily_summary["earnings"] = self.earnings - starting_earnings
            
            if day % 5 == 0:
                self.reflect_and_adapt()
                daily_summary["actions"].append(f"Changed strategy to: {self.strategy}")
            
            if random.random() < 0.1:
                events = [
                    "Got a callback for a speaking role!",
                    "Met an experienced producer who offered mentorship!",
                    "Short film got accepted into a festival!",
                    "Viral video brought industry attention!",
                    "Found potential investors for future projects!"
                ]
                special_event = random.choice(events)
                print(f"Special event: {special_event}")
                daily_summary["actions"].append(f"Special event: {special_event}")
            
            decision_log.append(daily_summary)
            time.sleep(0.1)
        
        print("\n=== 180 Day Journey Summary ===")
        print(json.dumps(self.get_status(), indent=2))
        
        if self.production_company:
            print("\n🎬 Production Company Status:")
            print(json.dumps(self.production_company, indent=2))
        
        print("\nKey Milestones:")
        milestone_days = [d for d in decision_log if any("MILESTONE" in str(a) for a in d.get("actions", []))]
        for day in milestone_days:
            print(f"Day {day['day']}:")
            for action in day["actions"]:
                if "MILESTONE" in str(action):
                    print(f"  {action}")
        
        print(f"\nTotal Earnings (Hope's 25% share): ${self.earnings:.2f}")
        print(f"Total Projects Completed: {self.jobs_completed}")
        print(f"Final Career Stage: {self.career_stage}")
        print("\nSkill Progression:")
        for skill, level in self.skills.items():
            print(f"{skill}: {level:.2f}")
            
        return decision_log

if __name__ == "__main__":
    hope = HopeAI()
    decision_log = hope.run(180) 