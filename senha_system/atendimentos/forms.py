from django import forms
from .models import Atendimento

class AtendimentoForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = "__all__"