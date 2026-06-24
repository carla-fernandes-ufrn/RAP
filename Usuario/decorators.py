import time
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode

def is_admin_check(user):
    try:
        tipo = user.usuario.tipo_usuario
        return tipo in ['Administrador', 'Root'] or user.is_superuser
    except:
        return user.is_superuser

def admin_otp_required(view_func):
    """
    Exige validação OTP para Administradores.
    Usuários Root têm passe livre.
    Outros usuários são repassados (a view lidará com a permissão).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('usuario:login')

        is_root = False
        try:
            is_root = user.usuario.tipo_usuario == 'Root' or user.is_superuser
        except:
            is_root = user.is_superuser
            
        if is_root:
            return view_func(request, *args, **kwargs)
            
        is_admin = False
        try:
            is_admin = user.usuario.tipo_usuario == 'Administrador'
        except:
            pass
            
        if is_admin:
            otp_valido_ate = request.session.get('admin_otp_valido_ate', 0)
            if time.time() > otp_valido_ate:
                # Sessão OTP expirada ou inexistente. Redireciona.
                base_url = reverse('usuario:validar_admin')
                query_string = urlencode({'next': request.get_full_path()})
                url = f"{base_url}?{query_string}"
                return redirect(url)
            
        return view_func(request, *args, **kwargs)

    return _wrapped_view
