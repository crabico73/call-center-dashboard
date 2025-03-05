from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import login_user, logout_user, current_user

def create_login_layout():
    """Create the login page layout"""
    return html.Div([
        html.Div([
            html.H3("Login to Call Center Dashboard", 
                   style={
                       "textAlign": "center",
                       "marginBottom": "2rem",
                       "color": "#202124"
                   }),
            html.Div([
                html.Label("Username", style={"marginBottom": "0.5rem", "color": "#202124"}),
                dcc.Input(
                    type="text",
                    id="username-input",
                    placeholder="Enter username",
                    n_submit=0,
                    style={
                        "width": "100%",
                        "padding": "8px 12px",
                        "marginBottom": "1rem",
                        "border": "1px solid #dadce0",
                        "borderRadius": "4px",
                        "fontSize": "14px"
                    }
                ),
                html.Label("Password", style={"marginBottom": "0.5rem", "color": "#202124"}),
                dcc.Input(
                    type="password",
                    id="password-input",
                    placeholder="Enter password",
                    n_submit=0,
                    style={
                        "width": "100%",
                        "padding": "8px 12px",
                        "marginBottom": "1.5rem",
                        "border": "1px solid #dadce0",
                        "borderRadius": "4px",
                        "fontSize": "14px"
                    }
                ),
                html.Button(
                    "Login",
                    id="login-button",
                    n_clicks=0,
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "backgroundColor": "#1a73e8",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "4px",
                        "cursor": "pointer",
                        "fontSize": "14px"
                    }
                ),
                html.Div(id="login-error", 
                        style={
                            "color": "#d93025",
                            "fontSize": "12px",
                            "textAlign": "center",
                            "marginTop": "1rem"
                        })
            ], style={
                "width": "100%",
                "maxWidth": "300px",
                "margin": "0 auto",
                "padding": "2rem",
                "backgroundColor": "white",
                "borderRadius": "8px",
                "boxShadow": "0 1px 2px 0 rgba(60,64,67,.3), 0 2px 6px 2px rgba(60,64,67,.15)"
            })
        ], style={
            "position": "absolute",
            "top": "50%",
            "left": "50%",
            "transform": "translate(-50%, -50%)",
            "width": "100%"
        })
    ], style={
        "width": "100vw",
        "height": "100vh",
        "backgroundColor": "#f8f9fa",
        "position": "relative"
    })

def create_user_menu(username):
    """Create the user menu dropdown"""
    return html.Div([
        html.Button(
            [username + " ▼"],
            id="user-menu-button",
            style={
                "backgroundColor": "transparent",
                "border": "none",
                "color": "#202124",
                "cursor": "pointer",
                "padding": "8px 12px"
            }
        ),
        dbc.Dropdown(
            id="user-menu-dropdown",
            options=[
                {"label": "Change Password", "value": "change-password"},
                {"label": "Logout", "value": "logout"}
            ],
            value="",
            style={
                "position": "absolute",
                "right": 0,
                "top": "100%"
            }
        )
    ], style={"position": "relative"})

def create_change_password_modal():
    """Create the change password modal"""
    return dbc.Modal([
        dbc.ModalHeader("Change Password"),
        dbc.ModalBody([
            dcc.Input(
                type="password",
                id="current-password-input",
                placeholder="Current Password",
                style={
                    "width": "100%",
                    "marginBottom": "1rem",
                    "padding": "8px 12px",
                    "border": "1px solid #dadce0",
                    "borderRadius": "4px"
                }
            ),
            dcc.Input(
                type="password",
                id="new-password-input",
                placeholder="New Password",
                style={
                    "width": "100%",
                    "marginBottom": "1rem",
                    "padding": "8px 12px",
                    "border": "1px solid #dadce0",
                    "borderRadius": "4px"
                }
            ),
            dcc.Input(
                type="password",
                id="confirm-password-input",
                placeholder="Confirm New Password",
                style={
                    "width": "100%",
                    "marginBottom": "1rem",
                    "padding": "8px 12px",
                    "border": "1px solid #dadce0",
                    "borderRadius": "4px"
                }
            ),
            html.Div(id="change-password-error", 
                    style={
                        "color": "#d93025",
                        "fontSize": "12px",
                        "marginTop": "0.5rem"
                    })
        ]),
        dbc.ModalFooter([
            html.Button(
                "Cancel",
                id="change-password-cancel",
                style={
                    "marginRight": "0.5rem",
                    "padding": "6px 12px",
                    "border": "1px solid #dadce0",
                    "borderRadius": "4px",
                    "backgroundColor": "white",
                    "cursor": "pointer"
                }
            ),
            html.Button(
                "Save",
                id="change-password-save",
                style={
                    "padding": "6px 12px",
                    "backgroundColor": "#1a73e8",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "4px",
                    "cursor": "pointer"
                }
            )
        ])
    ], id="change-password-modal") 