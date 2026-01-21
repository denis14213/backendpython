"""
Routes Médecin
"""

from controllers.medecin_controller import bp
from middleware.auth import role_required

# Appliquer la protection médecin à toutes les routes
for endpoint, view_func in bp.view_functions.items():
    bp.view_functions[endpoint] = role_required('medecin')(view_func)

