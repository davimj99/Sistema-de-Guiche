from django.db import migrations, models


def preencher_nomes_entregas(apps, schema_editor):
    EntregaEPI = apps.get_model("epis", "EntregaEPI")

    for entrega in EntregaEPI.objects.select_related(
        "funcionario",
        "epi",
    ):
        entrega.funcionario_nome = entrega.funcionario.nome
        entrega.epi_nome = entrega.epi.nome

        entrega.save(
            update_fields=[
                "funcionario_nome",
                "epi_nome",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "epis",
            "0003_alter_funcionario_cargo_alter_funcionario_matricula_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="entregaepi",
            name="funcionario_nome",
            field=models.CharField(max_length=150),
        ),
        migrations.AddField(
            model_name="entregaepi",
            name="epi_nome",
            field=models.CharField(max_length=100),
        ),
        migrations.RunPython(
            preencher_nomes_entregas,
            migrations.RunPython.noop,
        ),
    ]