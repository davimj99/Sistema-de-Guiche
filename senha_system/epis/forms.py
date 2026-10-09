from django import forms

from .models import EPI, Funcionario, EntregaEPI

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ("nome", "matricula", "setor", "cargo", "ativo")
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome completo",
            }),
            "matricula": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Matrícula",
            }),
            "setor": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Setor",
            }),
            "cargo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Cargo",
            }),
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-checkbox",
            }),
        }


class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = (
            "nome",
            "codigo",
            "categoria",
            "descricao",
            "unidade",
            "quantidade_estoque",
            "estoque_minimo",
            "ativo",
        )
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex.: Luva de proteção",
            }),
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Código do EPI",
            }),
            "categoria": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex.: Proteção das mãos",
            }),
            "descricao": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Descrição do equipamento",
                "rows": 4,
            }),
            "unidade": forms.Select(attrs={
                "class": "form-control",
            }),
            "quantidade_estoque": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "estoque_minimo": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-checkbox",
            }),
        }

class EntregaEPIForm(forms.ModelForm):

    class Meta:
        model = EntregaEPI

        fields = (
            "funcionario",
            "epi",
            "quantidade",
            "data_proxima_troca",
            "observacao",
        )

        widgets = {
            "funcionario": forms.Select(attrs={
                "class": "form-control",
            }),

            "epi": forms.Select(attrs={
                "class": "form-control",
            }),

            "quantidade": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),

            "data_proxima_troca": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "observacao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Observações sobre a entrega",
            }),
        }