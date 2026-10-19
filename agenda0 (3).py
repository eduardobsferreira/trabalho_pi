"""
agenda0.py - Agenda de Contatos (versao 0: sem persistencia)

PDS001 - Projeto Integrador em Analise e Desenvolvimento de Sistemas I
Fatec Sao Paulo - Prof. Walter Matheos Junior

Escopo desta versao:
  - CRUD completo de contatos (nome, e-mail, telefone) em memoria.
  - Sem arquivo, sem banco de dados, sem interface grafica (RNF07).

Convencao de codigo:
  - Somente caracteres ASCII: sem acentos, sem cedilha e sem simbolos
    graficos. Isso garante execucao identica em Linux e em Windows,
    inclusive em terminais com codificacao cp1252 (RNF06).
"""

import os
import re

# ---------------------------------------------------------------------
#  Configuracao e estado global
# ---------------------------------------------------------------------
CAPACIDADE = 100          # RNF03 - capacidade maxima da agenda
LARGURA = 66              # largura das linhas de separacao na tela

agenda: list[dict] = []   # RNF07 - unico deposito de dados (volatil)
ultimo_id: int = 0        # RN01 - contador que nunca diminui


# ---------------------------------------------------------------------
#  Interface de usuario (UI)
# ---------------------------------------------------------------------
def limpar() -> None:
    """Limpa a tela do terminal (Windows ou Unix)."""
    os.system("cls" if os.name == "nt" else "clear")


def linha(char: str = "-", largura: int = LARGURA) -> None:
    """Desenha uma linha horizontal de separacao."""
    print(char * largura)


def cabecalho(titulo: str) -> None:
    """Limpa a tela e desenha o cabecalho padrao com o titulo da operacao."""
    limpar()
    linha("=")
    print("AGENDA DE CONTATOS".center(LARGURA))
    linha("-")
    print("  " + titulo)
    linha("-")


def entrada(prompt: str, obrigatorio: bool = True) -> str:
    """Le um valor do teclado.

    Com obrigatorio=True, repete a leitura enquanto o valor for vazio.
    Ctrl+C e Ctrl+D propagam para o ponto de entrada, que encerra o
    programa com uma mensagem em vez de um traceback (RNF05).
    """
    while True:
        valor = input("  " + prompt).strip()
        if valor or not obrigatorio:
            return valor
        print("  [!] Campo obrigatorio. Tente novamente.")


def pausar() -> None:
    """Aguarda o ENTER do usuario antes de voltar ao menu."""
    entrada("Pressione ENTER para continuar...", obrigatorio=False)


def exibir_contato(c: dict, detalhe: bool = False) -> None:
    """Exibe um contato em uma linha; com detalhe=True, acrescenta o e-mail."""
    print(f"  [{c['id']:>3}]  {c['nome']:<25.25}  tel: {c['telefone']}")
    if detalhe:
        print(f"          e-mail: {c['email']}")


# ---------------------------------------------------------------------
#  Validacao
# ---------------------------------------------------------------------
RE_EMAIL = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", re.I)
RE_TELEFONE = re.compile(r"^[\d\s\(\)\-\+]{7,20}$")
RE_CEP = re.compile(r"^\d{5}-?\d{3}$")

def validar_email(email: str) -> bool:
    """RF08 - verifica se o e-mail esta em formato aceitavel."""
    return bool(RE_EMAIL.match(email))


def validar_telefone(tel: str) -> bool:
    """RF08 - verifica o formato e exige ao menos 8 digitos no telefone."""
    if not RE_TELEFONE.match(tel):
        return False
    digitos = re.sub(r"\D", "", tel)
    return len(digitos) >= 8

def validar_cep(cep: str) -> bool:
    """RF08 - verifica se o CEP tem 8 digitos, com hifen opcional."""
    return bool(RE_CEP.match(cep))


# ---------------------------------------------------------------------
#  Helpers de contato
# ---------------------------------------------------------------------
def proximo_id() -> int:
    """RN01 - devolve um identificador novo, sempre crescente.

    O contador nunca diminui: um id de contato excluido jamais e
    reaproveitado.
    """
    global ultimo_id
    ultimo_id += 1
    return ultimo_id


def buscar_por_id(cid: int) -> dict | None:
    """Devolve o contato com o id informado ou None se nao existir."""
    for c in agenda:
        if c["id"] == cid:
            return c
    return None


def ler_id(acao: str) -> dict | None:
    """Le um id do teclado e devolve o contato correspondente.

    Devolve None (e ja exibe a mensagem adequada) quando o valor digitado
    nao e um inteiro ou quando nenhum contato tem esse id.
    """
    valor = entrada(f"ID do contato a {acao}: ")
    if not valor.isdigit():
        print("\n  [!] ID invalido: digite apenas numeros.")
        return None

    contato = buscar_por_id(int(valor))
    if contato is None:
        print(f"\n  [!] Contato #{valor} nao encontrado.")
    return contato

def ler_endereco() -> dict:
    """Le do teclado os subcampos do endereco e devolve um dicionario."""
    rua = entrada("Rua         : ")
    numero = entrada("Numero      : ")
    complemento = entrada("Complemento : ", obrigatorio=False)

    while True:
        cep = entrada("CEP         : ")
        if validar_cep(cep):
            break
        print("  [!] CEP invalido. Exemplo: 01310-100")

    estado = entrada("Estado      : ")
    pais = entrada("Pais        : ")

    return {"rua": rua, "numero": numero, "complemento": complemento,
            "cep": cep, "estado": estado, "pais": pais}

# ---------------------------------------------------------------------
#  CRUD - logica de negocio
# ---------------------------------------------------------------------
def criar_contato() -> None:
    """RF01, RF02, RF08, RF09 - cadastra um novo contato."""
    cabecalho("NOVO CONTATO")

    if len(agenda) >= CAPACIDADE:                      # RF09 / RNF03
        print(f"\n  [!] Agenda cheia! Capacidade maxima: {CAPACIDADE} contatos.")
        pausar()
        return

    nome = entrada("Nome     : ")                      # RN02

    while True:                                        # RF08
        email = entrada("E-mail   : ")
        if validar_email(email):
            break
        print("  [!] E-mail invalido. Exemplo: usuario@email.com")

    while True:                                        # RF08
        telefone = entrada("Telefone : ")
        if validar_telefone(telefone):
            break
        print("  [!] Telefone invalido. Use ao menos 8 digitos.")

          print("\n  --- Endereco ---")
    endereco = ler_endereco()

    contato = {"id": proximo_id(), "nome": nome,       # RF02 / RN01
               "email": email, "telefone": telefone}
    agenda.append(contato)                             # RNF07 - so memoria

    print(f"\n  [ok] Contato #{contato['id']} salvo com sucesso!")
    pausar()


def listar_contatos() -> None:
    """RF03 - lista todos os contatos em ordem alfabetica de nome."""
    cabecalho("LISTA DE CONTATOS")

    if not agenda:
        print("\n  Nenhum contato cadastrado ainda.")
        pausar()
        return

    print(f"  {'ID':>4}  {'NOME':<25}  {'TELEFONE':<18}  {'E-MAIL':<28}")
    linha()
    for c in sorted(agenda, key=lambda x: x["nome"].lower()):   # RN05
        print(f"  {c['id']:>4}  {c['nome']:<25.25}  "
              f"{c['telefone']:<18.18}  {c['email']:<28.28}")
    linha()
    print(f"  Total: {len(agenda)} / {CAPACIDADE} contatos")
    pausar()


def buscar_contato() -> None:
    """RF04 - busca contatos por parte do nome ou do e-mail."""
    cabecalho("BUSCAR CONTATO")

    if not agenda:
        print("\n  Nenhum contato cadastrado ainda.")
        pausar()
        return

    termo = entrada("Buscar por nome ou e-mail: ").lower()
    resultados = [c for c in agenda
                  if termo in c["nome"].lower() or termo in c["email"].lower()]

    if not resultados:
        print("\n  Nenhum contato encontrado.")
    else:
        print(f"\n  {len(resultados)} resultado(s):\n")
        linha()
        for c in sorted(resultados, key=lambda x: x["nome"].lower()):
            exibir_contato(c, detalhe=True)
        linha()

    pausar()


def exibir_detalhes() -> None:
    """RF05 - exibe os dados completos de um contato a partir do id."""
    cabecalho("DETALHES DO CONTATO")

    if not agenda:
        print("\n  Nenhum contato cadastrado ainda.")
        pausar()
        return

    contato = ler_id("consultar")
    if contato is not None:
        print()
        linha()
        print(f"  ID       : {contato['id']}")
        print(f"  Nome     : {contato['nome']}")
        print(f"  E-mail   : {contato['email']}")
        print(f"  Telefone : {contato['telefone']}")
        linha()

    pausar()


def editar_contato() -> None:
    """RF06, RF08, RN03 - altera os dados de um contato existente."""
    cabecalho("EDITAR CONTATO")

    if not agenda:
        print("\n  Nenhum contato para editar.")
        pausar()
        return

    contato = ler_id("editar")
    if contato is None:
        pausar()
        return

    print(f"\n  Editando: {contato['nome']}")
    print("  (deixe em branco para manter o valor atual)\n")       # RN03

    novo_nome = entrada(f"Novo nome     [{contato['nome']}]: ",
                        obrigatorio=False)

    while True:                                                    # RF08
        novo_email = entrada(f"Novo e-mail   [{contato['email']}]: ",
                             obrigatorio=False)
        if not novo_email or validar_email(novo_email):
            break
        print("  [!] E-mail invalido.")

    while True:                                                    # RF08
        novo_tel = entrada(f"Novo telefone [{contato['telefone']}]: ",
                           obrigatorio=False)
        if not novo_tel or validar_telefone(novo_tel):
            break
        print("  [!] Telefone invalido.")

    if novo_nome:
        contato["nome"] = novo_nome
    if novo_email:
        contato["email"] = novo_email
    if novo_tel:
        contato["telefone"] = novo_tel

    print(f"\n  [ok] Contato #{contato['id']} atualizado!")
    pausar()


def excluir_contato() -> None:
    """RF07, RN04 - remove um contato apos confirmacao explicita."""
    cabecalho("EXCLUIR CONTATO")

    if not agenda:
        print("\n  Nenhum contato para excluir.")
        pausar()
        return

    contato = ler_id("excluir")
    if contato is None:
        pausar()
        return

    print(f"\n  Contato selecionado: {contato['nome']} | "
          f"{contato['email']} | {contato['telefone']}")

    confirmacao = entrada("Confirmar exclusao? (s/N): ",
                          obrigatorio=False).lower()

    if confirmacao == "s":                                         # RN04
        cid = contato["id"]
        agenda.remove(contato)
        print(f"\n  [ok] Contato #{cid} removido.")
    else:
        print("\n  [x] Exclusao cancelada.")

    pausar()


# ---------------------------------------------------------------------
#  Menu principal
# ---------------------------------------------------------------------
MENU = [
    ("1", "Adicionar contato", criar_contato),
    ("2", "Listar contatos", listar_contatos),
    ("3", "Buscar contato", buscar_contato),
    ("4", "Ver detalhes", exibir_detalhes),
    ("5", "Editar contato", editar_contato),
    ("6", "Excluir contato", excluir_contato),
    ("0", "Sair", None),
]


def menu_principal() -> None:
    """Exibe o menu em laco e chama a operacao escolhida."""
    while True:
        cabecalho("MENU PRINCIPAL")
        print(f"  Contatos: {len(agenda)} / {CAPACIDADE}\n")
        for chave, descricao, _ in MENU:
            print(f"  [{chave}]  {descricao}")
        linha()

        opcao = entrada("Opcao: ", obrigatorio=False)
        acao = next((fn for chave, _, fn in MENU if chave == opcao), None)

        if opcao == "0":
            limpar()
            print("\n  Ate logo!\n")
            break
        elif acao is None:
            print("  [!] Opcao invalida.")
            pausar()
        else:
            acao()


# ---------------------------------------------------------------------
#  Dados de demonstracao
# ---------------------------------------------------------------------
def carregar_demo() -> None:
    """Carrega tres contatos de exemplo usando o mesmo contador de ids."""
    demos = [
        ("Ana Silva", "ana@email.com", "(11) 91234-5678",
         {"rua": "Av. Paulista", "numero": "1000", "complemento": "Sala 5",
          "cep": "01310-100", "estado": "SP", "pais": "Brasil"}),
        ("Bruno Costa", "bruno@email.com", "(21) 98765-4321",
         {"rua": "Rua da Carioca", "numero": "50", "complemento": "",
          "cep": "20050-050", "estado": "RJ", "pais": "Brasil"}),
        ("Carla Mendes", "carla@email.com", "(31) 97654-3210",
         {"rua": "Av. Afonso Pena", "numero": "1500", "complemento": "Apto 301",
          "cep": "30130-005", "estado": "MG", "pais": "Brasil"}),
    ]
for nome, email, telefone, endereco in demos:
        agenda.append({"id": proximo_id(), "nome": nome,
                       "email": email, "telefone": telefone,
                       "endereco": endereco})
# ---------------------------------------------------------------------
#  Ponto de entrada
# ---------------------------------------------------------------------
if __name__ == "__main__":
    try:
        carregar_demo()
        menu_principal()
    except (KeyboardInterrupt, EOFError):                          # RNF05
        print("\n\n  Programa encerrado pelo usuario.\n")
