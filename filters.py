# Helper filters for Jinja2 templates
from datetime import datetime
from flask import Blueprint

# Create blueprint for filters
filters_blueprint = Blueprint('filters', __name__)

@filters_blueprint.app_template_filter('datetime')
def format_datetime(value):
    """Format a datetime object to string."""
    if isinstance(value, datetime):
        return value.strftime('%b %d, %Y')
    return value

@filters_blueprint.app_template_filter('shortdate')
def format_shortdate(value):
    """Format a datetime object to a short date string."""
    if isinstance(value, datetime):
        return value.strftime('%m/%d/%y')
    return value

@filters_blueprint.app_template_filter('time')
def format_time(value):
    """Format a datetime object to time only."""
    if isinstance(value, datetime):
        return value.strftime('%I:%M %p')
    return value

@filters_blueprint.app_template_filter('currency')
def format_currency(value):
    """Format a number as currency."""
    return f"₹ {value:,.2f}"

@filters_blueprint.app_template_filter('integer')
def format_integer(value):
    """Format a number with thousands separator."""
    return f"{int(value):,}"

@filters_blueprint.app_template_filter('percentage')
def format_percentage(value):
    """Format a decimal as percentage."""
    return f"{value:.1f}%"

@filters_blueprint.app_template_filter('status_color')
def status_color(status):
    """Return bootstrap color class based on status."""
    status = status.lower()
    if status in ['active', 'success', 'completed', 'resolved']:
        return 'success'
    elif status in ['pending', 'in progress', 'under investigation', 'warning']:
        return 'warning'
    elif status in ['error', 'failed', 'critical', 'danger']:
        return 'danger'
    return 'secondary'