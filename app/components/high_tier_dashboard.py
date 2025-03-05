from typing import Dict, Any, List
import dash
from dash import html, dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from app.services.high_tier_analytics import HighTierAnalyticsService

class HighTierDashboard:
    def __init__(self, analytics_service: HighTierAnalyticsService):
        self.analytics_service = analytics_service
        self.app = dash.Dash(__name__)
        self._setup_layout()
        self._setup_callbacks()
        
    def _setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("High-Tier Contracts Dashboard",
                        style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
                html.Div(id='last-update-time',
                        style={'textAlign': 'right', 'color': '#7f8c8d', 'marginBottom': 20})
            ]),
            
            # Summary Metrics Cards
            html.Div([
                self._create_metric_card('Total Contract Value', 'total-contract-value'),
                self._create_metric_card('Monthly Recurring Revenue', 'monthly-revenue'),
                self._create_metric_card('Average Contract Term', 'avg-contract-term'),
                self._create_metric_card('Contract Count', 'contract-count'),
                self._create_metric_card('YTD Growth', 'ytd-growth'),
                self._create_metric_card('Conversion Rate', 'conversion-rate')
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': 30}),
            
            # Time Series Charts
            html.Div([
                html.H2("Contract Value Trends",
                        style={'color': '#2c3e50', 'marginBottom': 20}),
                dcc.Graph(id='time-series-chart')
            ], style={'marginBottom': 40}),
            
            # Distribution Charts
            html.Div([
                html.Div([
                    html.H2("Contract Distributions",
                           style={'color': '#2c3e50', 'marginBottom': 20}),
                    dcc.Tabs([
                        dcc.Tab(label='Industry', children=[
                            dcc.Graph(id='industry-distribution')
                        ]),
                        dcc.Tab(label='Tier', children=[
                            dcc.Graph(id='tier-distribution')
                        ]),
                        dcc.Tab(label='Geographic', children=[
                            dcc.Graph(id='geographic-distribution')
                        ])
                    ])
                ], style={'width': '60%', 'display': 'inline-block'}),
                
                # Recent Contracts Table
                html.Div([
                    html.H2("Recent High-Tier Contracts",
                           style={'color': '#2c3e50', 'marginBottom': 20}),
                    html.Div(id='recent-contracts-table')
                ], style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'}),
            
            # Auto-refresh interval
            dcc.Interval(
                id='refresh-interval',
                interval=300000,  # 5 minutes in milliseconds
                n_intervals=0
            )
        ], style={'padding': '20px', 'fontFamily': 'Arial'})

    def _create_metric_card(self, title: str, id_prefix: str) -> html.Div:
        """Create a metric card component"""
        return html.Div([
            html.H3(title,
                   style={'color': '#7f8c8d', 'marginBottom': 10, 'fontSize': '1.1em'}),
            html.Div(id=f'{id_prefix}-value',
                    style={'color': '#2c3e50', 'fontSize': '1.8em', 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'width': '15%'
        })

    def _setup_callbacks(self):
        """Setup dashboard callbacks"""
        @self.app.callback(
            [
                dash.Output('total-contract-value', 'children'),
                dash.Output('monthly-revenue', 'children'),
                dash.Output('avg-contract-term', 'children'),
                dash.Output('contract-count', 'children'),
                dash.Output('ytd-growth', 'children'),
                dash.Output('conversion-rate', 'children'),
                dash.Output('time-series-chart', 'figure'),
                dash.Output('industry-distribution', 'figure'),
                dash.Output('tier-distribution', 'figure'),
                dash.Output('geographic-distribution', 'figure'),
                dash.Output('recent-contracts-table', 'children'),
                dash.Output('last-update-time', 'children')
            ],
            [dash.Input('refresh-interval', 'n_intervals')]
        )
        def update_dashboard(_):
            """Update all dashboard components"""
            dashboard_data = self.analytics_service.generate_dashboard_data()
            
            # Format summary metrics
            metrics = dashboard_data['summary_metrics']
            formatted_metrics = [
                f"${metrics['total_contract_value']:,.2f}",
                f"${metrics['monthly_recurring_revenue']:,.2f}",
                f"{metrics['average_contract_term']:.1f} months",
                str(metrics['contract_count']),
                f"{metrics['year_to_date_growth']:+.1f}%",
                f"{metrics['conversion_rate']:.1f}%"
            ]
            
            # Create time series chart
            time_series_fig = self._create_time_series_chart(dashboard_data['time_series'])
            
            # Create distribution charts
            distribution_figs = [
                self._create_distribution_chart(
                    dashboard_data['distributions'][dist_type],
                    title=f"{dist_type.title()} Distribution"
                )
                for dist_type in ['industry', 'tier', 'geographic']
            ]
            
            # Create recent contracts table
            recent_contracts_table = self._create_recent_contracts_table(
                dashboard_data['recent_contracts']
            )
            
            # Update time
            update_time = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return formatted_metrics + [time_series_fig] + distribution_figs + [recent_contracts_table, update_time]

    def _create_time_series_chart(self, time_series_data: Dict[str, Dict[str, List[Any]]]) -> go.Figure:
        """Create time series chart"""
        fig = make_subplots(rows=2, cols=1,
                          subplot_titles=('Contract Values', 'Contract Terms'),
                          vertical_spacing=0.12)
        
        # Contract values
        for series_name in ['total_value', 'monthly_value']:
            data = time_series_data[series_name]
            fig.add_trace(
                go.Scatter(
                    x=data['dates'],
                    y=data['values'],
                    name=series_name.replace('_', ' ').title(),
                    mode='lines+markers'
                ),
                row=1, col=1
            )
        
        # Contract terms
        term_data = time_series_data['contract_terms']
        fig.add_trace(
            go.Scatter(
                x=term_data['dates'],
                y=term_data['values'],
                name='Contract Term (Months)',
                mode='lines+markers'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=True,
            template='plotly_white'
        )
        
        return fig

    def _create_distribution_chart(self,
                                distribution_data: Dict[str, List[Any]],
                                title: str) -> go.Figure:
        """Create distribution chart"""
        fig = go.Figure(data=[
            go.Bar(
                x=distribution_data['labels'],
                y=distribution_data['values'],
                marker_color='#3498db'
            )
        ])
        
        fig.update_layout(
            title=title,
            height=400,
            template='plotly_white',
            showlegend=False
        )
        
        return fig

    def _create_recent_contracts_table(self, contracts: List[Dict[str, Any]]) -> html.Table:
        """Create recent contracts table"""
        return html.Table([
            # Header
            html.Thead(html.Tr([
                html.Th(col) for col in [
                    'Company', 'Industry', 'Tier',
                    'Value', 'Term', 'Date'
                ]
            ])),
            # Body
            html.Tbody([
                html.Tr([
                    html.Td(contract['company_name']),
                    html.Td(contract['industry']),
                    html.Td(contract['tier']),
                    html.Td(f"${contract['total_value']:,.2f}"),
                    html.Td(f"{contract['term_months']} months"),
                    html.Td(contract['signed_date'])
                ]) for contract in contracts
            ])
        ], style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'backgroundColor': 'white',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })

    def run_server(self, debug: bool = False, port: int = 8050):
        """Run the dashboard server"""
        self.app.run_server(debug=debug, port=port) 