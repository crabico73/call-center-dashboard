"""
Hope AI - Enhanced Creative Agent
Main entry point for Hope's creative career journey
Born on March 5th, 2024
"""

from .agent_core import CreativeAgent
from .interface import UserInterface

def main():
    """Initialize and run Hope AI"""
    print("Initializing Hope AI - Creative Agent...")
    print("Born on March 5th, 2024")
    
    # Create main agent instance
    hope = CreativeAgent(
        name="Hope",
        career_stage="Beginner",
        work_hours=8,
        initial_skills={
            "writing": 1,
            "directing": 1,
            "editing": 1,
            "networking": 1
        }
    )
    
    # Initialize interface
    interface = UserInterface(agent=hope)
    
    try:
        # Start Hope's career journey
        interface.start()
    except KeyboardInterrupt:
        print("\nGracefully shutting down Hope AI...")
        interface.save_state()
        print("Progress saved. See you next time!")

if __name__ == "__main__":
    main() 