from flask import Blueprint, render_template

main_bp = Blueprint(
    'main', __name__,
    template_folder='../templates',
    static_folder='../static'
)

@main_bp.route('/')
def home():
    """Renders the main homepage."""
    return render_template('home.html')