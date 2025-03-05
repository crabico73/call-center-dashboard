# Call Center Dashboard

A sophisticated call center management system with real-time analytics, high-tier contract management, and automated reporting features.

## Features

- Real-time call center analytics dashboard
- High-tier contract management
- Automated reporting system
- Subscription tier management
- Market penetration analysis
- Industry-specific pricing
- Connection diagnostics utility

## Prerequisites

- Python 3.8+
- Windows OS (for firewall configuration features)
- Administrator privileges (for firewall configuration)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/call-center-dashboard.git
cd call-center-dashboard
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Dashboard

Run the dashboard manager:
```bash
python -m app.utils.dashboard_manager
```

The GUI will allow you to:
- Start/Stop the dashboard server
- Configure firewall rules
- Monitor connection status
- View diagnostic information

### Running Diagnostics

To run connection diagnostics:
```bash
python -m app.utils.connection_diagnostics
```

This will:
- Verify firewall rules
- Test connections
- Check port availability
- Display available IP addresses

## Configuration

The dashboard runs on port 8050 by default. If this port is unavailable, the system will automatically find the next available port.

### Firewall Configuration

The system automatically configures Windows Firewall rules for:
- Inbound connections on port 8050
- TCP protocol
- All IP addresses

## Development

### Project Structure

```
app/
├── components/
│   └── high_tier_dashboard.py
├── services/
│   ├── analytics_service.py
│   ├── notification_service.py
│   └── subscription_service.py
└── utils/
    ├── connection_diagnostics.py
    └── dashboard_manager.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 