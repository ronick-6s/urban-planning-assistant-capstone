"""
Admin Financial Tools Module

Provides administrative access to financial metrics and data.
Requires admin role for access.
"""

from access_control import get_user

def get_all_financial_metrics(user_id: str):
    """Display all financial metrics - admin only."""
    user = get_user(user_id)
    if not user or "admin" not in user["roles"]:
        print("\nAccess Denied: Administrative privileges required.")
        return
    
    try:
        from tabulate import tabulate
        
        metrics = [
            ["Budget Forecast (5-year)", "$125M → $158M", "4.8% annual growth"],
            ["Infrastructure Maintenance", "$8.5M/year", "Increasing 3.2% annually"],
            ["Development Investment Risk", "Moderate", "Downtown: Low, Suburban: Medium"],
            ["Municipal Bond Performance", "AA rating", "4.2% yield projection"],
            ["Property Tax Revenue", "$42M current", "Projected $51M by 2028"],
            ["Transit Investment ROI", "3.2:1 ratio", "Property value uplift"],
        ]
        
        print("\n" + "="*80)
        print("ADMINISTRATIVE FINANCIAL METRICS")
        print("="*80)
        print(tabulate(metrics, headers=["Metric", "Current Value", "Projection/Notes"], tablefmt="grid"))
        print("="*80 + "\n")
    except ImportError:
        print("\nFinancial metrics available. Install 'tabulate' package for formatted output.")
        print("\nKey Metrics:")
        print("- Budget Forecast (5-year): $125M → $158M (4.8% annual growth)")
        print("- Infrastructure Maintenance: $8.5M/year (Increasing 3.2% annually)")
        print("- Development Investment Risk: Moderate overall")
        print("- Municipal Bond Performance: AA rating, 4.2% yield projection")


def get_specific_financial_metric(user_id: str, metric_name: str):
    """Display a specific financial metric - admin only."""
    user = get_user(user_id)
    if not user or "admin" not in user["roles"]:
        print("\nAccess Denied: Administrative privileges required.")
        return
    
    metrics_data = {
        "budget forecast": {
            "name": "Five-Year Budget Forecast",
            "details": [
                "Current Budget: $125M",
                "Year 1 Projection: $130.5M (+4.4%)",
                "Year 2 Projection: $136.8M (+4.8%)",
                "Year 3 Projection: $143.5M (+4.9%)",
                "Year 4 Projection: $150.6M (+4.9%)",
                "Year 5 Projection: $158.0M (+4.9%)",
            ]
        },
        "investment risk": {
            "name": "Development Investment Risk Analysis",
            "details": [
                "Downtown District: Low Risk (High demand, established infrastructure)",
                "Waterfront District: Low-Medium Risk (Growing market, transit access)",
                "Suburban Areas: Medium Risk (Lower density, infrastructure needs)",
                "Overall Portfolio Risk: Moderate",
                "Mitigation: Diversified development across districts",
            ]
        },
    }
    
    metric_key = metric_name.lower()
    if metric_key in metrics_data:
        data = metrics_data[metric_key]
        print(f"\n{'='*60}")
        print(f"{data['name']}")
        print(f"{'='*60}")
        for detail in data['details']:
            print(f"  {detail}")
        print(f"{'='*60}\n")
    else:
        print(f"\nMetric '{metric_name}' not found. Available metrics:")
        print("  - budget forecast")
        print("  - investment risk")