from agent_core import CreativeAgent
import json
from typing import List, Dict
import time

class AgentInterface:
    def __init__(self):
        self.agent = CreativeAgent()
        self.command_history = []

    def process_command(self, command: str, *args) -> Dict:
        """Process user commands and return formatted responses"""
        self.command_history.append((command, args, time.time()))
        
        commands = {
            "status": self._get_status,
            "analyze": self._analyze_market,
            "plan": self._create_project_plan,
            "improve": self._improve_skill,
            "next": self._get_next_steps,
            "goals": self._show_goals,
            "help": self._show_help
        }
        
        if command in commands:
            return commands[command](*args)
        return {"error": "Unknown command. Type 'help' for available commands."}

    def _get_status(self) -> Dict:
        """Get current agent status"""
        return self.agent.generate_report()

    def _analyze_market(self, content_type: str = "animation") -> Dict:
        """Analyze market opportunities"""
        return self.agent.analyze_market_opportunity(content_type)

    def _create_project_plan(self, project_type: str = "animation", duration: int = 30) -> Dict:
        """Create a project plan"""
        return self.agent.plan_project(project_type, duration)

    def _improve_skill(self, skill: str, hours: int = 1) -> Dict:
        """Improve a specific skill"""
        result = self.agent.improve_skill(skill, hours)
        return {"result": result, "current_level": self.agent.skills.get(skill, 0)}

    def _get_next_steps(self) -> Dict:
        """Get recommended next steps"""
        return {"next_steps": self.agent.get_next_steps()}

    def _show_goals(self) -> Dict:
        """Show current goals"""
        return {"goals": self.agent.goals}

    def _show_help(self) -> Dict:
        """Show available commands"""
        return {
            "available_commands": {
                "status": "Show current agent status and resources",
                "analyze [content_type]": "Analyze market opportunities",
                "plan [project_type] [duration]": "Create a project plan",
                "improve [skill] [hours]": "Improve a specific skill",
                "next": "Get recommended next steps",
                "goals": "Show current goals",
                "help": "Show this help message"
            }
        }

def format_response(response: Dict) -> str:
    """Format response for display"""
    return json.dumps(response, indent=2)

def main():
    interface = AgentInterface()
    print("Creative Agent Interface")
    print("Type 'help' for available commands")
    
    while True:
        try:
            user_input = input("\nEnter command: ").strip().split()
            if not user_input:
                continue
            
            command = user_input[0].lower()
            args = user_input[1:]
            
            if command == "quit":
                break
                
            response = interface.process_command(command, *args)
            print("\nResponse:")
            print(format_response(response))
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 