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
from app.dashboard.payment_views import create_payment_form, create_payment_success
from app.services.payment_service import PaymentService
import os
import sys
import webbrowser
from threading import Timer
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask import request, session
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from app.services.business_rules import BusinessRules

# Initialize services
data_service = None
auth_service = None
payment_service = None
business_rules = None
login_manager = None

def initialize_services():
    """Initialize all services"""
    global data_service, auth_service, payment_service, business_rules, login_manager
    
    try:
        data_service = DataService()
        auth_service = AuthService()
        payment_service = PaymentService()
        business_rules = BusinessRules()
        
        # Setup Flask-Login
        login_manager = LoginManager()
        
        @login_manager.user_loader
        def load_user(user_id):
            return auth_service.get_user(int(user_id))
        
        return True
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        return False

def open_browser(port, browser_name=None):
    """Open the browser after a short delay
    Args:
        port (int): Port number for the server
        browser_name (str, optional): Browser to use ('firefox', 'chrome', 'edge', 'safari', etc.)
    """
    url = f'http://localhost:{port}/login'
    try:
        if browser_name:
            # Get list of available browsers
            available_browsers = webbrowser._browsers.keys()
            print("\nAvailable browsers:", ", ".join(available_browsers))
            
            if browser_name.lower() in available_browsers:
                browser = webbrowser.get(browser_name.lower())
                browser.open(url)
            else:
                print(f"\nRequested browser '{browser_name}' not found. Using system default.")
                webbrowser.open(url)
        else:
            # Use system default browser
            webbrowser.open(url)
    except Exception as e:
        print(f"\nWarning: Browser error: {e}. Using system default.")
        webbrowser.open(url)

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    update_title=None,
    title="Call Center Dashboard",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    url_base_pathname='/'
)

# Configure the Flask server
server = app.server

# Add custom headers to bypass proxy authentication
@server.after_request
def add_header(response):
    response.headers['Proxy-Authenticate'] = 'Basic'
    response.headers['WWW-Authenticate'] = 'Basic'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

server.config.update(
    SECRET_KEY='call-center-dashboard-key',
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_PROTECTION='strong',
    # Add proxy bypass settings
    PROXY_SKIP_VERIFY=True,
    PREFERRED_URL_SCHEME='http'
)

# Add CORS support with specific origins
CORS(server, 
     resources={
         r"/*": {
             "origins": ["http://127.0.0.1:8050", "http://localhost:8050"],
             "supports_credentials": True
         }
     })

# Initialize services before creating layout
if not initialize_services():
    print("Failed to initialize services. Exiting...")
    sys.exit(1)

# Initialize test database with sample data
data_service.create_test_database()

# Initialize login manager
login_manager.init_app(server)
login_manager.login_view = "/login"

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
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='auth-store', storage_type='session'),
    html.Div(id='page-content')
])

def get_dashboard_data():
    """Get all data needed for the dashboard"""
    if not is_authenticated():
        return None
    return {
        'daily_calls': data_service.get_daily_calls(),
        'current_stats': data_service.get_current_day_stats(),
        'hourly_data': data_service.get_hourly_distribution(),
        'contract_stats': business_rules.get_daily_stats()
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
    
    # Add new contract goal card
    contract_stats = initial_data['contract_stats']
    contract_progress = (contract_stats['current'] / contract_stats['goal']) * 100 if contract_stats['goal'] > 0 else 0
    
    return dbc.Container([
        # Header with user menu
        dbc.Row([
            dbc.Col(html.H1("Call Center Dashboard", className="mb-4"), width=6),
            dbc.Col([
                create_user_menu(current_user.username),
                dbc.Button(
                    "Payment Setup",
                    id="show-payment-form",
                    color="success",
                    className="ms-3"
                )
            ], width=6, className="text-right d-flex justify-content-end align-items-center")
        ], className="mt-4"),
        
        # KPI Cards
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Total Calls Today", className="card-title"),
                    html.H2(f"{initial_data['current_stats']['total_calls']:,.0f}", className="text-primary")
                ])
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Success Rate", className="card-title"),
                    html.H2(f"{initial_data['current_stats']['success_rate']:.1%}", className="text-success")
                ])
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Avg Duration", className="card-title"),
                    html.H2(f"{initial_data['current_stats']['avg_duration']:.0f}s", className="text-info")
                ])
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Daily Contract Goal", className="card-title"),
                    html.Div([
                        html.H2([
                            f"{contract_stats['current']}/{contract_stats['goal']}",
                            html.Span(" Contracts", className="fs-6 ms-2")
                        ], className="mb-2"),
                        dbc.Progress(
                            value=min(100, contract_progress),
                            color="success" if contract_stats['current'] >= contract_stats['goal'] else "primary",
                            className="mb-2",
                            style={"height": "8px"}
                        ),
                        html.P([
                            html.Strong(f"{contract_stats['remaining']} more"),
                            " needed today"
                        ] if contract_stats['remaining'] > 0 else [
                            html.Strong("Daily Goal Reached!", className="text-success")
                        ], className="mb-0 small")
                    ])
                ])
            ]), width=3),
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
        create_change_password_modal(),
        
        # Add payment form modal
        dbc.Modal([
            dbc.ModalHeader("Payment Setup"),
            dbc.ModalBody(create_payment_form()),
        ], id="payment-modal", size="xl")
    ], fluid=True)

# Single callback to handle page content
@app.callback(
    [Output('page-content', 'children'),
     Output('auth-store', 'data')],
    [Input('url', 'pathname'),
     Input('login-button', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value'),
     State('auth-store', 'data')],
    prevent_initial_call=True
)
def render_page_content(pathname, n_clicks, username, password, auth_data):
    """Handle page routing and authentication"""
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Initialize auth data
    if auth_data is None:
        auth_data = {'authenticated': False}
    
    # Handle login button click
    if triggered_id == 'login-button' and n_clicks:
        if not username or not password:
            return create_login_layout(error="Please enter both username and password"), auth_data
            
        try:
            user = auth_service.authenticate_user(username, password)
            if user:
                login_user(user)
                session['user_id'] = user.id
                session.permanent = True
                auth_data = {'authenticated': True}
                return create_dashboard_layout(), auth_data
        except Exception as e:
            print(f"Login error: {e}")
            return create_login_layout(error="An error occurred during login"), auth_data
        
        return create_login_layout(error="Invalid username or password"), auth_data
    
    # Handle page routing based on authentication status
    if not auth_data.get('authenticated'):
        return create_login_layout(), auth_data
    
    return create_dashboard_layout(), auth_data

# Callback for logout
@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('auth-store', 'data', allow_duplicate=True)],
    Input('user-menu-dropdown', 'value'),
    prevent_initial_call=True
)
def handle_menu_click(value):
    if value == 'logout':
        logout_user()
        session.clear()
        return '/login', {'authenticated': False}
    return dash.no_update, dash.no_update

# Callback for change password modal
@app.callback(
    [Output("change-password-modal", "is_open"),
     Output("change-password-error", "children")],
    [Input("user-menu-dropdown", "value"),
     Input("change-password-cancel", "n_clicks"),
     Input("change-password-save", "n_clicks")],
    [State("current-password-input", "value"),
     State("new-password-input", "value"),
     State("confirm-password-input", "value"),
     State("change-password-modal", "is_open")],
    prevent_initial_call=True
)
def handle_change_password(dropdown_value, cancel, save, current_pw, new_pw, confirm_pw, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "user-menu-dropdown" and dropdown_value == "change-password":
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

# Add callback to update URL after login/logout
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('page-content', 'children')],
    prevent_initial_call=True
)
def update_url(content):
    """Update URL based on page content"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
        
    if isinstance(content, dict) and content.get('props', {}).get('id') == 'redirect-to-login':
        return '/login'
    elif is_authenticated():
        return '/'
    return dash.no_update

# Update payment form callback
@app.callback(
    [Output("payment-modal", "is_open"),
     Output("page-content", "children"),
     Output("payment-form-status", "children")],
    [Input("show-payment-form", "n_clicks"),
     Input("submit-payment-form", "n_clicks"),
     Input("clear-payment-form", "n_clicks")],
    [State("business-name", "value"),
     State("dba-name", "value"),
     State("tax-id", "value"),
     State("years-business", "value"),
     State("bank-name", "value"),
     State("account-type", "value"),
     State("routing-number", "value"),
     State("account-number", "value"),
     State("signer-name", "value"),
     State("signer-title", "value"),
     State("signer-email", "value"),
     State("signer-phone", "value"),
     State("agreement-checkbox", "checked"),
     State("payment-modal", "is_open")],
    prevent_initial_call=True
)
def handle_payment_form(show_clicks, submit_clicks, clear_clicks,
                       business_name, dba_name, tax_id, years_business,
                       bank_name, account_type, routing_number, account_number,
                       signer_name, signer_title, signer_email, signer_phone,
                       agreement_accepted, is_open):
    """Handle payment form interactions"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, dash.no_update, ""
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "show-payment-form":
        # Check if we can accept more contracts today
        if not business_rules.can_accept_more_contracts():
            stats = business_rules.get_daily_stats()
            return False, dash.no_update, html.Div([
                html.H4("Daily Goal Reached", className="text-success"),
                html.P([
                    f"We have reached our daily goal of {stats['goal']} contracts. ",
                    "Please try again tomorrow."
                ])
            ])
        return not is_open, dash.no_update, ""
    
    if button_id == "clear-payment-form":
        return True, dash.no_update, ""
    
    if button_id == "submit-payment-form":
        # Check if we can still accept contracts
        if not business_rules.can_accept_more_contracts():
            return True, dash.no_update, html.Div(
                "Daily contract limit reached. Please try again tomorrow.",
                className="text-danger"
            )
        
        # Validate required fields
        required_fields = {
            "business_name": business_name,
            "tax_id": tax_id,
            "bank_name": bank_name,
            "account_type": account_type,
            "routing_number": routing_number,
            "account_number": account_number,
            "signer_name": signer_name,
            "signer_title": signer_title,
            "signer_email": signer_email,
            "signer_phone": signer_phone
        }
        
        if not all(required_fields.values()) or not agreement_accepted:
            return True, dash.no_update, html.Div(
                "Please fill in all required fields and accept the agreement.",
                className="text-danger"
            )
        
        try:
            # Save payment information
            payment_data = {
                "business_name": business_name,
                "dba_name": dba_name,
                "tax_id": tax_id,
                "years_business": years_business,
                "bank_name": bank_name,
                "account_type": account_type,
                "routing_number": routing_number,
                "account_number": account_number,
                "signer_name": signer_name,
                "signer_title": signer_title,
                "signer_email": signer_email,
                "signer_phone": signer_phone,
                "agreement_accepted": agreement_accepted
            }
            
            # Save payment info and record contract
            if payment_service.save_payment_info(payment_data):
                if business_rules.add_contract(business_name):
                    return False, create_payment_success(), ""
            
            return True, dash.no_update, html.Div(
                "An error occurred while saving your information. Please try again.",
                className="text-danger"
            )
        except Exception as e:
            print(f"Error processing payment form: {e}")
            return True, dash.no_update, html.Div(
                "An error occurred while processing your request.",
                className="text-danger"
            )
    
    return is_open, dash.no_update, ""

def run_dashboard(debug=True, port=8050, browser=None):
    """Run the dashboard server
    Args:
        debug (bool): Whether to run in debug mode
        port (int): Port to run the server on
        browser (str, optional): Browser to use ('firefox', 'chrome', 'edge', 'safari', etc.)
    """
    print("\n" + "="*50)
    print("Starting dashboard server...")
    
    # Detect if running behind proxy
    proxy_url = os.environ.get('PROXY_URL', f'http://127.0.0.1:{port}')
    print(f"Dashboard will be available at: {proxy_url}")
    
    print("\nDefault login credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("="*50 + "\n")
    
    # Only open browser on initial run, not on debug reload
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        Timer(2, lambda: open_browser(port, browser)).start()
    
    try:
        app.run_server(
            debug=debug,
            port=port,
            host='0.0.0.0',  # Listen on all interfaces
            dev_tools_hot_reload=False
        )
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
    # Let the system use the default browser
    run_dashboard()
    
    # Or uncomment one of these lines to specify a browser:
    # run_dashboard(browser='firefox')
    # run_dashboard(browser='chrome')
    # run_dashboard(browser='edge')
    # run_dashboard(browser='safari') 