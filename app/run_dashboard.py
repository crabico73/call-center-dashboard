from app.services.high_tier_analytics import HighTierAnalyticsService
from app.components.high_tier_dashboard import HighTierDashboard
from app.utils.firewall_config import configure_firewall
import sys

def main():
    # Configure port
    port = 8050
    
    # Configure firewall
    if not configure_firewall(port):
        print("\nDashboard may not be accessible. To fix this:")
        print("1. Run this script as administrator, or")
        print("2. Manually allow port 8050 in Windows Firewall")
        print("3. Press Ctrl+C to exit if needed\n")
    
    # Initialize services
    analytics_service = HighTierAnalyticsService()
    
    # Create and run dashboard
    dashboard = HighTierDashboard(analytics_service)
    dashboard.run_server(debug=True, port=port)

if __name__ == "__main__":
    main() 