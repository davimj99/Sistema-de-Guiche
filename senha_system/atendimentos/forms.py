from django import forms
from django.utils import timezone
from .models import Atendimento
from filas.models import Senha


class AtendimentoForm(forms.ModelForm):

    class Meta:
        model = Atendimento
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hoje = timezone.localdate()

        self.fields["senha"].queryset = Senha.objects.filter(
            criada_em__date=hoje
        ).order_by("criada_em", "id")