from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime

def create_payment_form():
    """Create a payment information collection form"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Payment Authorization Form", className="mb-4"),
                html.P("Please complete all fields for payment processing setup.", className="text-muted mb-4")
            ])
        ]),
        
        # Company Information
        dbc.Row([
            dbc.Col([
                html.H4("Company Information", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Legal Business Name *"),
                        dbc.Input(id="business-name", type="text", required=True)
                    ], width=6),
                    dbc.Col([
                        html.Label("DBA (if different)"),
                        dbc.Input(id="dba-name", type="text")
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Tax ID (EIN) *"),
                        dbc.Input(id="tax-id", type="text", required=True)
                    ], width=6),
                    dbc.Col([
                        html.Label("Years in Business"),
                        dbc.Input(id="years-business", type="number", min=0)
                    ], width=6)
                ])
            ], width=12, className="mb-4")
        ]),
        
        # Banking Information
        dbc.Row([
            dbc.Col([
                html.H4("Banking Information", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Bank Name *"),
                        dbc.Input(id="bank-name", type="text", required=True)
                    ], width=6),
                    dbc.Col([
                        html.Label("Account Type *"),
                        dbc.Select(
                            id="account-type",
                            options=[
                                {"label": "Checking", "value": "checking"},
                                {"label": "Savings", "value": "savings"}
                            ],
                            required=True
                        )
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Routing Number *"),
                        dbc.Input(id="routing-number", type="text", required=True, maxLength=9)
                    ], width=6),
                    dbc.Col([
                        html.Label("Account Number *"),
                        dbc.Input(id="account-number", type="text", required=True)
                    ], width=6)
                ])
            ], width=12, className="mb-4")
        ]),
        
        # Authorized Signer Information
        dbc.Row([
            dbc.Col([
                html.H4("Authorized Signer Information", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Full Name *"),
                        dbc.Input(id="signer-name", type="text", required=True)
                    ], width=6),
                    dbc.Col([
                        html.Label("Title/Position *"),
                        dbc.Input(id="signer-title", type="text", required=True)
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Email *"),
                        dbc.Input(id="signer-email", type="email", required=True)
                    ], width=6),
                    dbc.Col([
                        html.Label("Phone *"),
                        dbc.Input(id="signer-phone", type="tel", required=True)
                    ], width=6)
                ])
            ], width=12, className="mb-4")
        ]),
        
        # Authorization Agreement
        dbc.Row([
            dbc.Col([
                html.H4("Authorization Agreement", className="mb-3"),
                dbc.Checkbox(
                    id="agreement-checkbox",
                    label=[
                        "I authorize ",
                        html.Strong("Call Center Dashboard"),
                        " to initiate payment processing using the information provided above. I acknowledge that I am an authorized signer on the account specified."
                    ],
                    className="mb-3"
                ),
                html.Div([
                    dbc.Button("Submit", id="submit-payment-form", color="primary", className="me-2"),
                    dbc.Button("Clear Form", id="clear-payment-form", color="secondary"),
                ], className="d-flex justify-content-start"),
                html.Div(id="payment-form-status", className="mt-3")
            ], width=12)
        ])
    ], className="py-4")

def create_payment_success():
    """Create success message after form submission"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Thank You!", className="text-success mb-4"),
                html.P([
                    "Your payment information has been securely recorded. ",
                    "A confirmation email will be sent to the provided email address."
                ], className="mb-4"),
                html.Div([
                    html.P([
                        html.Strong("Reference Number: "),
                        html.Span(datetime.now().strftime("%Y%m%d-%H%M%S"))
                    ]),
                    html.P([
                        html.Strong("Submission Date: "),
                        html.Span(datetime.now().strftime("%B %d, %Y"))
                    ])
                ], className="bg-light p-3 rounded"),
                html.Div([
                    dbc.Button(
                        "Return to Dashboard",
                        id="return-to-dashboard",
                        color="primary",
                        className="mt-4"
                    )
                ])
            ], width={"size": 8, "offset": 2}, className="text-center")
        ])
    ], className="py-5") 