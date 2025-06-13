from django.contrib import admin
from .models import Acervo  # <- Só importamos Acervo agora

# Remova ou comente qualquer linha que tente registrar 'TipoAcervo'
# admin.site.register(TipoAcervo)  # Apague ou comente

admin.site.register(Acervo)
