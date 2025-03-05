import os

def load_analytics_config():
    """Load analytics and reporting configuration"""
    return {
        "email_config": {
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "smtp_username": os.getenv("SMTP_USERNAME"),
            "smtp_password": os.getenv("SMTP_PASSWORD"),
            "recipient_email": os.getenv("REPORT_RECIPIENT_EMAIL"),
            "cc_emails": os.getenv("REPORT_CC_EMAILS", "").split(","),
        },
        "reporting_schedule": {
            "weekly_report_day": "friday",
            "weekly_report_time": "17:00",
            "timezone": os.getenv("TIMEZONE", "UTC"),
        },
        "predictive_model_config": {
            "min_data_points": 3,
            "max_polynomial_degree": 3,
            "confidence_threshold": 0.7,
            "feature_importance_threshold": 0.1
        },
        "visualization_config": {
            "chart_theme": "plotly_white",
            "color_scheme": [
                "#1f77b4",  # blue
                "#ff7f0e",  # orange
                "#2ca02c",  # green
                "#d62728",  # red
                "#9467bd",  # purple
                "#8c564b",  # brown
                "#e377c2",  # pink
                "#7f7f7f",  # gray
            ],
            "default_height": 600,
            "default_width": 800
        }
    } 