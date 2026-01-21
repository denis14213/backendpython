"""
Routes Secrétaire
"""

from controllers.secretaire_controller import bp
from middleware.auth import role_required

# Appliquer la protection secrétaire/admin à toutes les routes
for endpoint, view_func in bp.view_functions.items():
    bp.view_functions[endpoint] = role_required('secretaire', 'admin')(view_func)

