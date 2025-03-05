import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import dash_bootstrap_components as dbc
from app.services.data_service import DataService
from app.services.auth_service import AuthService
from app.dashboard.auth_views import create_login_layout, create_user_menu, create_change_password_modal
import os
import sys
import webbrowser
from threading import Timer
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask import request, session
from functools import wraps

# Initialize services
data_service = None
auth_service = None
login_manager = None

def initialize_services():
    """Initialize all services"""
    global data_service, auth_service, login_manager
    
    try:
        data_service = DataService()
        auth_service = AuthService()
        
        # Setup Flask-Login
        login_manager = LoginManager()
        
        @login_manager.user_loader
        def load_user(user_id):
            return auth_service.get_user(int(user_id))
        
        return True
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        return False

def open_browser(port):
    """Open the browser after a short delay"""
    webbrowser.open(f'http://localhost:{port}/')

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    update_title=None,  # Disable the "Updating..." browser title
    title="Call Center Dashboard"  # Set the page title
)

# Configure the Flask server
server = app.server
server.config.update(
    SECRET_KEY='call-center-dashboard-key',  # Use a consistent secret key
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
)

# Initialize services before creating layout
if not initialize_services():
    print("Failed to initialize services. Exiting...")
    sys.exit(1)

# Initialize login manager
login_manager.init_app(server)
login_manager.login_view = "/login"
login_manager.session_protection = "strong"

def is_authenticated():
    """Check if user is authenticated"""
    try:
        return current_user.is_authenticated and current_user.is_active
    except:
        return False

def require_login(f):
    """Decorator to require login for dash callbacks"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return dash.no_update
        return f(*args, **kwargs)
    return decorated_function

# Add URL location component at the app level
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content'),
    dcc.Store(id='login-status', storage_type='session', data={'authenticated': False})
])

def get_dashboard_data():
    """Get all data needed for the dashboard"""
    if not is_authenticated():
        return None
    return {
        'daily_calls': data_service.get_daily_calls(),
        'current_stats': data_service.get_current_day_stats(),
        'hourly_data': data_service.get_hourly_distribution()
    }

# Create charts
def create_charts(df, hourly_data):
    # Rename columns for consistency
    df = df.rename(columns={
        'total_calls': 'calls',
        'avg_duration': 'duration'
    })
    
    calls_fig = px.line(
        df, 
        x='date', 
        y='calls', 
        title='Daily Call Volume',
        template='plotly_white'
    )
    calls_fig.update_traces(line_color='#1a73e8')
    
    success_fig = px.line(
        df, 
        x='date', 
        y='success_rate', 
        title='Success Rate',
        template='plotly_white'
    )
    success_fig.update_traces(line_color='#0f9d58')
    success_fig.update_layout(yaxis_tickformat='.0%')
    
    duration_fig = px.line(
        df, 
        x='date', 
        y='duration', 
        title='Average Call Duration (seconds)',
        template='plotly_white'
    )
    duration_fig.update_traces(line_color='#ea4335')
    
    # Create hourly distribution chart
    hourly_fig = go.Figure()
    hourly_fig.add_trace(go.Bar(
        x=hourly_data['hour'],
        y=hourly_data['call_count'],
        name='Call Volume',
        marker_color='#1a73e8'
    ))
    hourly_fig.add_trace(go.Scatter(
        x=hourly_data['hour'],
        y=hourly_data['success_rate'] * hourly_data['call_count'].max(),
        name='Success Rate',
        yaxis='y2',
        line=dict(color='#0f9d58')
    ))
    hourly_fig.update_layout(
        title='Hourly Call Distribution',
        yaxis2=dict(
            title='Success Rate',
            overlaying='y',
            side='right',
            tickformat='.0%',
            range=[0, 1]
        ),
        template='plotly_white'
    )
    
    return calls_fig, success_fig, duration_fig, hourly_fig

def create_dashboard_layout():
    """Create the main dashboard layout"""
    if not is_authenticated():
        return dcc.Location(pathname='/login', id='redirect-to-login')
    
    # Get initial data for authenticated users
    initial_data = get_dashboard_data()
    if not initial_data:
        return dcc.Location(pathname='/login', id='redirect-to-login')
        
    calls_fig, success_fig, duration_fig, hourly_fig = create_charts(
        initial_data['daily_calls'], 
        initial_data['hourly_data']
    )
    
    return dbc.Container([
        # Header with user menu
        dbc.Row([
            dbc.Col(html.H1("Call Center Dashboard", className="mb-4"), width=8),
            dbc.Col(create_user_menu(current_user.username), width=4, className="text-right")
        ], className="mt-4"),
        
        # KPI Cards
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Total Calls Today", className="card-title"),
                    html.H2(f"{initial_data['current_stats']['total_calls']:,.0f}", className="text-primary")
                ])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Success Rate", className="card-title"),
                    html.H2(f"{initial_data['current_stats']['success_rate']:.1%}", className="text-success")
                ])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Avg Duration", className="card-title"),
                    html.H2(f"{initial_data['current_stats']['avg_duration']:.0f}s", className="text-info")
                ])
            ]), width=4),
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col(dcc.Graph(
                id='graph-0',
                figure=calls_fig
            ), width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(dcc.Graph(
                id='graph-1',
                figure=success_fig
            ), width=6),
            dbc.Col(dcc.Graph(
                id='graph-2',
                figure=duration_fig
            ), width=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(dcc.Graph(
                id='graph-3',
                figure=hourly_fig
            ), width=12)
        ], className="mb-4"),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # in milliseconds (1 minute)
            n_intervals=0
        ),
        
        # Footer
        dbc.Row([
            dbc.Col(html.Hr()),
            dbc.Col(html.P(
                "Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                className="text-muted text-center",
                id="last-update"
            ))
        ]),
        
        # Add change password modal
        create_change_password_modal()
    ], fluid=True)

# Callback for URL routing
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/login' or not is_authenticated():
        return create_login_layout()
    return create_dashboard_layout()

# Callback for login
@app.callback(
    [Output('url', 'pathname'),
     Output('login-error', 'children')],
    [Input('login-button', 'n_clicks'),
     Input('username-input', 'n_submit'),
     Input('password-input', 'n_submit')],
    [State('username-input', 'value'),
     State('password-input', 'value')],
    prevent_initial_call=True
)
def login(n_clicks, username_submit, password_submit, username, password):
    triggered = [p['prop_id'] for p in dash.callback_context.triggered]
    if not triggered or (not n_clicks and not username_submit and not password_submit):
        return dash.no_update, dash.no_update
    
    if not username or not password:
        return dash.no_update, "Please enter both username and password"
    
    user = auth_service.authenticate_user(username, password)
    if user:
        login_user(user)
        return '/dashboard', ""
    return dash.no_update, "Invalid username or password"

# Callback for logout
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        logout_user()
        session.clear()
        return '/login'
    return dash.no_update

# Callback for change password modal
@app.callback(
    [Output("change-password-modal", "is_open"),
     Output("change-password-error", "children")],
    [Input("change-password-button", "n_clicks"),
     Input("change-password-cancel", "n_clicks"),
     Input("change-password-save", "n_clicks")],
    [State("current-password-input", "value"),
     State("new-password-input", "value"),
     State("confirm-password-input", "value"),
     State("change-password-modal", "is_open")],
    prevent_initial_call=True
)
def handle_change_password(show_modal, cancel, save, current_pw, new_pw, confirm_pw, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "change-password-button":
        return True, ""
    elif button_id == "change-password-cancel":
        return False, ""
    elif button_id == "change-password-save":
        if not all([current_pw, new_pw, confirm_pw]):
            return True, "Please fill in all fields"
        if new_pw != confirm_pw:
            return True, "New passwords do not match"
        if not auth_service.authenticate_user(current_user.username, current_pw):
            return True, "Current password is incorrect"
        
        if auth_service.change_password(current_user.id, new_pw):
            return False, ""
        return True, "Failed to change password"
    
    return is_open, ""

# Callback for data updates
@app.callback(
    [Output('last-update', 'children')] +
    [Output(f'graph-{i}', 'figure') for i in range(4)],
    Input('interval-component', 'n_intervals')
)
@require_login
def update_graphs(n):
    data = get_dashboard_data()
    if not data:
        return [dash.no_update] * 5
        
    calls_fig, success_fig, duration_fig, hourly_fig = create_charts(
        data['daily_calls'], 
        data['hourly_data']
    )
    
    timestamp = "Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [timestamp, calls_fig, success_fig, duration_fig, hourly_fig]

def run_dashboard(debug=True, port=8050):
    """Run the dashboard server"""
    print("\n" + "="*50)
    print("Starting dashboard server...")
    print(f"Dashboard will be available at: http://localhost:{port}")
    print("\nDefault login credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("="*50 + "\n")
    
    # Open browser after a short delay
    Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}/login')).start()
    
    try:
        app.run_server(debug=debug, port=port, host='localhost')
    except Exception as e:
        print(f"\nError starting server: {e}")
        if "Address already in use" in str(e):
            print(f"\nPort {port} is already in use. This might mean:")
            print("1. The dashboard is already running in another window")
            print("2. Another application is using this port")
            print("\nTry:")
            print("1. Close other instances of the dashboard")
            print("2. Use a different port by modifying the port number")
        sys.exit(1)

if __name__ == '__main__':
    run_dashboard() 