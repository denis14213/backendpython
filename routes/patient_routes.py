"""
Routes Patient
"""

from controllers.patient_controller import bp
from middleware.auth import login_required

# Appliquer la protection login à toutes les routes sauf inscription
for endpoint, view_func in bp.view_functions.items():
    if endpoint != 'register':
        bp.view_functions[endpoint] = login_required(view_func)

