from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import schedule
import time
import threading
from app.services.roi_tracking import ROITrackingService, ImplementationPhase

@dataclass
class PredictiveModel:
    feature_columns: List[str]
    target_column: str
    model: Any
    polynomial_degree: int = 1
    r_squared: float = 0.0

class AnalyticsReportingService:
    def __init__(self,
                 roi_service: ROITrackingService,
                 email_config: Dict[str, Any]):
        self.roi_service = roi_service
        self.email_config = email_config
        self.predictive_models: Dict[str, PredictiveModel] = {}
        self._setup_scheduler()

    def _setup_scheduler(self):
        """Setup weekly report scheduler"""
        schedule.every().friday.at("17:00").do(self.generate_and_send_weekly_report)
        
        # Run scheduler in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

    def train_predictive_models(self):
        """Train predictive models using historical implementation data"""
        implementations = list(self.roi_service.implementation_data.values())
        if not implementations:
            return
        
        # Prepare training data
        df = pd.DataFrame([
            {
                "industry": impl.industry,
                "call_volume": impl.initial_call_volume,
                "subscription_tier": impl.subscription_tier,
                "implementation_days": sum(impl.phase_durations.values(), timedelta()).days if impl.completion_date else None,
                "cost_savings": (sum(impl.traditional_costs.values()) - sum(impl.actual_costs.values())) 
                    if impl.completion_date else None,
                "efficiency_gain": statistics.mean(impl.efficiency_metrics.values()) * 100 
                    if impl.efficiency_metrics and impl.completion_date else None,
                "quality_improvement": statistics.mean(impl.quality_metrics.values()) * 100 
                    if impl.quality_metrics and impl.completion_date else None
            }
            for impl in implementations
        ])
        
        # Remove incomplete implementations
        df = df.dropna()
        
        if len(df) < 3:  # Need minimum data points for meaningful predictions
            return
        
        # Encode categorical variables
        df = pd.get_dummies(df, columns=["industry", "subscription_tier"])
        
        # Train models for different metrics
        target_metrics = [
            "implementation_days",
            "cost_savings",
            "efficiency_gain",
            "quality_improvement"
        ]
        
        feature_columns = [col for col in df.columns 
                         if col not in target_metrics]
        
        for target in target_metrics:
            X = df[feature_columns]
            y = df[target]
            
            # Try different polynomial degrees
            best_model = None
            best_r2 = -float('inf')
            best_degree = 1
            
            for degree in [1, 2, 3]:
                poly = PolynomialFeatures(degree=degree)
                X_poly = poly.fit_transform(X)
                
                model = LinearRegression()
                model.fit(X_poly, y)
                r2 = model.score(X_poly, y)
                
                if r2 > best_r2:
                    best_r2 = r2
                    best_model = model
                    best_degree = degree
            
            self.predictive_models[target] = PredictiveModel(
                feature_columns=feature_columns,
                target_column=target,
                model=best_model,
                polynomial_degree=best_degree,
                r_squared=best_r2
            )

    def predict_implementation_metrics(self,
                                    industry: str,
                                    call_volume: int,
                                    subscription_tier: str) -> Dict[str, Any]:
        """Predict implementation metrics for new client"""
        if not self.predictive_models:
            self.train_predictive_models()
            if not self.predictive_models:
                return {}
        
        # Prepare input data
        input_data = pd.DataFrame([{
            "call_volume": call_volume,
            "industry": industry,
            "subscription_tier": subscription_tier
        }])
        
        # Generate predictions
        predictions = {}
        for metric, model in self.predictive_models.items():
            # Encode categorical variables
            input_encoded = pd.get_dummies(input_data)
            
            # Add missing columns from training
            for col in model.feature_columns:
                if col not in input_encoded.columns:
                    input_encoded[col] = 0
            
            # Reorder columns to match training data
            input_encoded = input_encoded[model.feature_columns]
            
            # Apply polynomial transformation
            poly = PolynomialFeatures(degree=model.polynomial_degree)
            input_poly = poly.fit_transform(input_encoded)
            
            # Make prediction
            pred = model.model.predict(input_poly)[0]
            predictions[metric] = {
                "predicted_value": round(pred, 2),
                "confidence": round(model.r_squared * 100, 2)
            }
        
        return predictions

    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate comprehensive weekly analytics report"""
        current_date = datetime.now()
        week_start = current_date - timedelta(days=current_date.weekday() + 7)
        week_end = week_start + timedelta(days=6)
        
        # Get all implementations
        implementations = self.roi_service.implementation_data.values()
        
        # Filter for active implementations this week
        active_implementations = [
            impl for impl in implementations
            if not impl.completion_date or impl.completion_date >= week_start
        ]
        
        # Calculate weekly metrics
        weekly_metrics = {
            "date_range": {
                "start": week_start.isoformat(),
                "end": week_end.isoformat()
            },
            "active_implementations": len(active_implementations),
            "completed_this_week": sum(
                1 for impl in active_implementations
                if impl.completion_date and impl.completion_date >= week_start
            ),
            "total_cost_savings": sum(
                sum(impl.traditional_costs.values()) - sum(impl.actual_costs.values())
                for impl in active_implementations
                if impl.completion_date
            ),
            "phase_breakdown": self._calculate_phase_breakdown(active_implementations),
            "industry_breakdown": self._calculate_industry_breakdown(active_implementations),
            "performance_summary": self._calculate_performance_summary(active_implementations),
            "predictions": self._generate_prediction_insights()
        }
        
        return weekly_metrics

    def generate_and_send_weekly_report(self):
        """Generate and email weekly report"""
        report_data = self.generate_weekly_report()
        
        # Generate HTML report
        html_content = self._generate_html_report(report_data)
        
        # Generate visualizations
        figures = self._generate_report_visualizations(report_data)
        
        # Send email
        self._send_report_email(html_content, figures)

    def _calculate_phase_breakdown(self,
                                implementations: List[Any]) -> Dict[str, Any]:
        """Calculate implementation phase breakdown"""
        phase_counts = {phase.value: 0 for phase in ImplementationPhase}
        
        for impl in implementations:
            current_phase = self.roi_service._get_current_phase(impl)
            phase_counts[current_phase] += 1
        
        return phase_counts

    def _calculate_industry_breakdown(self,
                                   implementations: List[Any]) -> Dict[str, Any]:
        """Calculate industry-wise implementation metrics"""
        industry_metrics = {}
        
        for impl in implementations:
            if impl.industry not in industry_metrics:
                industry_metrics[impl.industry] = {
                    "active_count": 0,
                    "completed_count": 0,
                    "total_savings": 0,
                    "avg_efficiency": 0
                }
            
            metrics = industry_metrics[impl.industry]
            metrics["active_count"] += 1
            
            if impl.completion_date:
                metrics["completed_count"] += 1
                metrics["total_savings"] += (
                    sum(impl.traditional_costs.values()) - 
                    sum(impl.actual_costs.values())
                )
                if impl.efficiency_metrics:
                    metrics["avg_efficiency"] = statistics.mean(
                        impl.efficiency_metrics.values()
                    ) * 100
        
        return industry_metrics

    def _calculate_performance_summary(self,
                                    implementations: List[Any]) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        completed = [impl for impl in implementations if impl.completion_date]
        
        if not completed:
            return {}
        
        return {
            "avg_implementation_days": statistics.mean([
                sum(impl.phase_durations.values(), timedelta()).days
                for impl in completed
            ]),
            "avg_cost_savings": statistics.mean([
                sum(impl.traditional_costs.values()) - sum(impl.actual_costs.values())
                for impl in completed
            ]),
            "avg_efficiency_gain": statistics.mean([
                statistics.mean(impl.efficiency_metrics.values()) * 100
                for impl in completed
                if impl.efficiency_metrics
            ]) if any(impl.efficiency_metrics for impl in completed) else 0,
            "avg_quality_improvement": statistics.mean([
                statistics.mean(impl.quality_metrics.values()) * 100
                for impl in completed
                if impl.quality_metrics
            ]) if any(impl.quality_metrics for impl in completed) else 0
        }

    def _generate_prediction_insights(self) -> Dict[str, Any]:
        """Generate insights from predictive models"""
        if not self.predictive_models:
            return {}
        
        insights = {}
        for metric, model in self.predictive_models.items():
            insights[metric] = {
                "model_accuracy": round(model.r_squared * 100, 2),
                "significant_factors": self._identify_significant_factors(model)
            }
        
        return insights

    def _identify_significant_factors(self, model: PredictiveModel) -> List[str]:
        """Identify most significant factors in prediction"""
        if not model.model.coef_.any():
            return []
        
        # Get absolute coefficient values
        coef_importance = np.abs(model.model.coef_)
        
        # Get top 3 most important features
        top_indices = np.argsort(coef_importance)[-3:]
        
        return [model.feature_columns[i] for i in top_indices]

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report content"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
                .metric {{ font-size: 24px; color: #2c3e50; }}
                .label {{ font-size: 14px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <h1>Weekly Implementation Analytics Report</h1>
            <p>Week of {report_data['date_range']['start']} to {report_data['date_range']['end']}</p>
            
            <div class="section">
                <h2>Implementation Overview</h2>
                <div class="metric">{report_data['active_implementations']}</div>
                <div class="label">Active Implementations</div>
                <div class="metric">{report_data['completed_this_week']}</div>
                <div class="label">Completed This Week</div>
                <div class="metric">${report_data['total_cost_savings']:,.2f}</div>
                <div class="label">Total Cost Savings</div>
            </div>
            
            <div class="section">
                <h2>Performance Summary</h2>
                {self._format_performance_metrics(report_data['performance_summary'])}
            </div>
            
            <div class="section">
                <h2>Industry Breakdown</h2>
                {self._format_industry_metrics(report_data['industry_breakdown'])}
            </div>
            
            <div class="section">
                <h2>Predictive Insights</h2>
                {self._format_prediction_insights(report_data['predictions'])}
            </div>
        </body>
        </html>
        """
        return html

    def _generate_report_visualizations(self,
                                     report_data: Dict[str, Any]) -> List[go.Figure]:
        """Generate report visualizations"""
        figures = []
        
        # Implementation Phase Distribution
        phase_fig = go.Figure(data=[
            go.Bar(
                x=list(report_data['phase_breakdown'].keys()),
                y=list(report_data['phase_breakdown'].values())
            )
        ])
        phase_fig.update_layout(
            title="Implementation Phase Distribution",
            xaxis_title="Phase",
            yaxis_title="Number of Implementations"
        )
        figures.append(phase_fig)
        
        # Industry Performance
        industry_data = report_data['industry_breakdown']
        industry_fig = make_subplots(rows=2, cols=1)
        
        industry_fig.add_trace(
            go.Bar(
                x=list(industry_data.keys()),
                y=[data['active_count'] for data in industry_data.values()],
                name="Active Implementations"
            ),
            row=1, col=1
        )
        
        industry_fig.add_trace(
            go.Bar(
                x=list(industry_data.keys()),
                y=[data['total_savings'] for data in industry_data.values()],
                name="Total Savings"
            ),
            row=2, col=1
        )
        
        industry_fig.update_layout(
            title="Industry Performance Metrics",
            height=600
        )
        figures.append(industry_fig)
        
        return figures

    def _send_report_email(self, html_content: str, figures: List[go.Figure]):
        """Send report email with visualizations"""
        msg = MIMEMultipart()
        msg['Subject'] = f"Weekly Implementation Analytics Report - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = self.email_config['smtp_username']
        msg['To'] = self.email_config['recipient_email']
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach visualizations
        for i, fig in enumerate(figures):
            img_bytes = fig.to_image(format="png")
            img_attachment = MIMEApplication(img_bytes)
            img_attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=f'visualization_{i+1}.png'
            )
            msg.attach(img_attachment)
        
        # Send email
        with smtplib.SMTP(self.email_config['smtp_server'],
                         self.email_config['smtp_port']) as server:
            server.starttls()
            server.login(
                self.email_config['smtp_username'],
                self.email_config['smtp_password']
            )
            server.send_message(msg)

    @staticmethod
    def _format_performance_metrics(metrics: Dict[str, float]) -> str:
        """Format performance metrics for HTML display"""
        if not metrics:
            return "<p>No completed implementations in this period</p>"
        
        return f"""
        <div class="metric">{metrics['avg_implementation_days']:.1f} days</div>
        <div class="label">Average Implementation Time</div>
        <div class="metric">${metrics['avg_cost_savings']:,.2f}</div>
        <div class="label">Average Cost Savings</div>
        <div class="metric">{metrics['avg_efficiency_gain']:.1f}%</div>
        <div class="label">Average Efficiency Gain</div>
        <div class="metric">{metrics['avg_quality_improvement']:.1f}%</div>
        <div class="label">Average Quality Improvement</div>
        """

    @staticmethod
    def _format_industry_metrics(metrics: Dict[str, Dict[str, Any]]) -> str:
        """Format industry metrics for HTML display"""
        html = "<table border='1' cellpadding='5'>"
        html += "<tr><th>Industry</th><th>Active</th><th>Completed</th><th>Total Savings</th><th>Avg Efficiency</th></tr>"
        
        for industry, data in metrics.items():
            html += f"""
            <tr>
                <td>{industry}</td>
                <td>{data['active_count']}</td>
                <td>{data['completed_count']}</td>
                <td>${data['total_savings']:,.2f}</td>
                <td>{data['avg_efficiency']:.1f}%</td>
            </tr>
            """
        
        html += "</table>"
        return html

    @staticmethod
    def _format_prediction_insights(insights: Dict[str, Dict[str, Any]]) -> str:
        """Format prediction insights for HTML display"""
        if not insights:
            return "<p>No prediction models available yet</p>"
        
        html = "<table border='1' cellpadding='5'>"
        html += "<tr><th>Metric</th><th>Model Accuracy</th><th>Key Factors</th></tr>"
        
        for metric, data in insights.items():
            html += f"""
            <tr>
                <td>{metric}</td>
                <td>{data['model_accuracy']}%</td>
                <td>{', '.join(data['significant_factors'])}</td>
            </tr>
            """
        
        html += "</table>"
        return html 