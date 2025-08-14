""""""
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.apps import apps
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    """Cria grupos padrão e associa permissões automaticamente"""

    if sender.name != 'core':  # só roda quando o core for migrado
        return

    group_permissions = {
        "ADMIN": ["add", "change", "delete", "view"],  # todos os actions para todos os modelos
        "FUNCIONARIO": ["view", "add", "change"],      # ações mais restritas
        "MOTORISTA": ["view"],
        "ENCARREGADO": ["view"]
    }

    roles = list(group_permissions.keys())

    for role in roles:
        group, created = Group.objects.get_or_create(name=role)
        if created:
            print(f"Grupo criado: {role}")

        permissions_to_add = []

        # Percorre todos os modelos do projeto
        for model_class in apps.get_models():
            model_name = model_class._meta.model_name
            app_label = model_class._meta.app_label

            # Define ações permitidas de acordo com o role
            actions = group_permissions[role]

            for action in actions:
                codename = f"{action}_{model_name}"
                try:
                    perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
                    permissions_to_add.append(perm)
                except Permission.DoesNotExist:
                    print(f"⚠ Permissão não encontrada: {app_label}.{codename}")

        group.permissions.set(permissions_to_add)
        group.save()

    print("✅ Grupos e permissões padrão criados/atualizados com sucesso!")

# @reciver(post_migrate)
# def create_default_roles(sender, **kwargs):
#     """Cria grupos padrao e associa permissoes"""

#     if sender.nome == 'core':
#         roles = ['ADMIN', 'FUNCIONARIO', 'MOTORISTA','ENCARREGADO']

#         for role in roles:
#             grou, create = Group.objects.get_or_create(name=role)

#             if create:
#                 print(f'Groupo criado: {role}')

#             # Adiciona permissoes diferentes para cada role
#             if role =='ADMIN':
#                 # Admin recebe todas as permissoes
#                 permissions == Permission.objects.all()

#             elif role == 'FUNCIONARIO':
#                 # Funcionario pode adicionar, ver e alterar alguns modelos
#                 permissions == Permission.objects.filter(
#                     codename__startswith='core_'
#                 )
#             elif role == 'MOTORISTA':
#                 #
#                 permissions == Permission.objects.filter(
#                     codename__startwith='view_'
#                 )
#             elif role == 'ENCARREGADO':
#                 Permissions ==Permission.objects.filter(
#                     codename__startwith='view_'
#                 )

#             group.permissions.get(permissions)
#             group.save()

# @receiver(post_migrate)
# def create_default_groups(sender, **kwargs):
#     """
#     Cria grupos padrões com permissões associadas
#     sempre que as migrations forem aplicadas.
#     """
#     if sender.name == "auth":  # Evita rodar para todos os apps
#         return

#     # Definição de grupos e permissões
#     group_permissions = {
#         "ADMIN": {
#             "alunos": ["add_aluno", "change_aluno", "delete_aluno", "view_aluno"],
#             "financeiro": ["add_pagamento", "change_pagamento", "delete_pagamento", "view_pagamento"],
#             "transporte": ["add_carro", "change_carro", "delete_carro", "view_carro",
#                            "add_rota", "change_rota", "delete_rota", "view_rota"],
#             "usuarios": ["add_user", "change_user", "delete_user", "view_user"],
#         },
#         "FUNCIONARIO": {
#             "alunos": ["view_aluno"],
#             "financeiro": ["view_pagamento"],
#             "transporte": ["view_carro", "view_rota"],
#         },
#         "MOTORISTA": {
#             "transporte": ["view_carro", "view_rota"],
#             "alunos": ["view_aluno"],
#         },
#         "ENCARREGADO": {
#             "alunos": ["view_aluno"],
#             "financeiro": ["view_pagamento"],
#         },
#     }

#     for group_name, perms_dict in group_permissions.items():
#         group, _ = Group.objects.get_or_create(name=group_name)

#         for app_label, codename_list in perms_dict.items():
#             for codename in codename_list:
#                 try:
#                     perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
#                     group.permissions.add(perm)
#                 except Permission.DoesNotExist:
#                     print(f"⚠ Permissão não encontrada: {app_label}.{codename}")

#     print("✅ Grupos e permissões padrão criados/atualizados com sucesso!")
