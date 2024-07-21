from django.contrib import admin
from PlanoAula.models import PlanoAula, FotoRobo, VideoRobo, FotoExecucao, VideoExecucao, LikePlanoAula, ExecucaoPlanoAula

admin.site.register(PlanoAula)
admin.site.register(FotoRobo)
admin.site.register(VideoRobo)
admin.site.register(FotoExecucao)
admin.site.register(VideoExecucao)
admin.site.register(LikePlanoAula)
admin.site.register(ExecucaoPlanoAula)
