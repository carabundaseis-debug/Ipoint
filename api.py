"""
Cliente da API do Ipoint (Supabase).
Faz login/registro e todas as operações de conta pela internet,
em vez de guardar tudo só no celular.
"""
import requests
import hashlib
import json
import os

SUPABASE_URL = "https://jvjbssjiqqbzcazbdxax.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_l5uT28KXelNEtesmh9zQDA_LHKqjfv3"

_access_token = None
_refresh_token = None
_user_email = None


class ApiError(Exception):
    pass


def _headers(autenticado=True):
    h = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }
    if autenticado and _access_token:
        h["Authorization"] = f"Bearer {_access_token}"
    else:
        h["Authorization"] = f"Bearer {SUPABASE_ANON_KEY}"
    return h


def esta_logado():
    return _access_token is not None


def usuario_atual():
    return _user_email


def _erro_de(resposta):
    try:
        dados = resposta.json()
        return (
            dados.get("error_description")
            or dados.get("msg")
            or dados.get("message")
            or dados.get("hint")
            or str(dados)
        )
    except Exception:
        return resposta.text or "Erro de comunicação com o servidor."


def registrar(email, senha):
    """Retorna True se já entrou logado, False se precisa confirmar o e-mail antes."""
    global _access_token, _refresh_token, _user_email
    email = email.strip().lower()
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            json={"email": email, "password": senha},
            headers=_headers(autenticado=False),
            timeout=20,
        )
    except requests.RequestException:
        raise ApiError("Não foi possível conectar. Verifique sua internet.")

    dados = r.json() if r.text else {}
    if r.status_code >= 400:
        raise ApiError(_erro_de(r))

    if dados.get("access_token"):
        _access_token = dados["access_token"]
        _refresh_token = dados.get("refresh_token")
        _user_email = email
        return True
    return False


def login(email, senha):
    global _access_token, _refresh_token, _user_email
    email = email.strip().lower()
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            json={"email": email, "password": senha},
            headers=_headers(autenticado=False),
            timeout=20,
        )
    except requests.RequestException:
        raise ApiError("Não foi possível conectar. Verifique sua internet.")

    dados = r.json() if r.text else {}
    if r.status_code >= 400:
        raise ApiError(_erro_de(r))

    _access_token = dados["access_token"]
    _refresh_token = dados.get("refresh_token")
    _user_email = email


def logout():
    global _access_token, _refresh_token, _user_email
    _access_token = None
    _refresh_token = None
    _user_email = None


def _get(caminho, params=None):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{caminho}", headers=_headers(), params=params, timeout=20)
    except requests.RequestException:
        raise ApiError("Não foi possível conectar. Verifique sua internet.")
    if r.status_code >= 400:
        raise ApiError(_erro_de(r))
    return r.json()


def _post(caminho, corpo, prefer=None):
    headers = _headers()
    if prefer:
        headers["Prefer"] = prefer
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/{caminho}", headers=headers, json=corpo, timeout=20)
    except requests.RequestException:
        raise ApiError("Não foi possível conectar. Verifique sua internet.")
    if r.status_code >= 400:
        raise ApiError(_erro_de(r))
    return r.json() if r.text else None


def _patch(caminho, corpo):
    try:
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/{caminho}", headers=_headers(), json=corpo, timeout=20)
    except requests.RequestException:
        raise ApiError("Não foi possível conectar. Verifique sua internet.")
    if r.status_code >= 400:
        raise ApiError(_erro_de(r))


def _rpc(nome, parametros):
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/{nome}", headers=_headers(), json=parametros, timeout=20)
    except requests.RequestException:
        raise ApiError("Não foi possível conectar. Verifique sua internet.")
    if r.status_code >= 400:
        raise ApiError(_erro_de(r))
    return r.json() if r.text else None


def listar_contas():
    return _get("contas", params={"select": "*", "order": "id.asc"})


def obter_conta(conta_id):
    resultado = _get("contas", params={"id": f"eq.{conta_id}", "select": "*"})
    return resultado[0] if resultado else None


def criar_conta(nome, saldo_inicial=0.0, categoria="comum"):
    resultado = _post(
        "contas",
        {"nome": nome, "saldo": float(saldo_inicial), "categoria": categoria},
        prefer="return=representation",
    )
    conta = resultado[0]
    if saldo_inicial and float(saldo_inicial) != 0:
        _post("transacoes", {
            "conta_id": conta["id"], "tipo": "entrada",
            "valor": float(saldo_inicial), "descricao": "Saldo inicial",
        })
    return conta["id"]


def depositar(conta_id, valor, descricao="Depósito"):
    valor = float(valor)
    if valor <= 0:
        raise ApiError("O valor precisa ser maior que zero.")
    conta = obter_conta(conta_id)
    if not conta:
        raise ApiError("Conta não encontrada.")
    novo_saldo = float(conta["saldo"]) + valor
    _patch(f"contas?id=eq.{conta_id}", {"saldo": novo_saldo})
    _post("transacoes", {"conta_id": conta_id, "tipo": "entrada", "valor": valor, "descricao": descricao})


def transferir_para_destino(destino, valor, descricao=None):
    _rpc("transferir_para_destino", {
        "destino": destino.strip(),
        "valor_transferido": float(valor),
        "descricao_transferencia": descricao,
    })


def minha_chave():
    """Busca a chave aleatória do usuário logado (para mostrar/gerar o QR code)."""
    resultado = _get("perfis", params={"select": "chave,email"})
    if resultado:
        return resultado[0].get("chave")
    return None


def sou_admin():
    resultado = _get("perfis", params={"select": "eh_admin"})
    if resultado:
        return bool(resultado[0].get("eh_admin"))
    return False


def listar_avisos(limite=30):
    return _get("avisos", params={"select": "*", "order": "criado_em.desc", "limit": limite})


def criar_aviso(titulo, mensagem):
    _post("avisos", {"titulo": titulo, "mensagem": mensagem})


# ---------------------------------------------------------------------------
# PIN local (login rápido sem digitar e-mail/senha de novo no mesmo aparelho)
# ---------------------------------------------------------------------------

def _arquivo_sessao():
    try:
        from kivy.app import App
        base = App.get_running_app().user_data_dir
    except Exception:
        base = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "sessao_local.json")


def salvar_pin(pin):
    if not (_refresh_token and _user_email):
        raise ApiError("Faça login normal antes de configurar um PIN.")
    dados = {
        "email": _user_email,
        "refresh_token": _refresh_token,
        "pin_hash": hashlib.sha256(pin.encode()).hexdigest(),
    }
    with open(_arquivo_sessao(), "w") as f:
        json.dump(dados, f)


def tem_pin_configurado():
    caminho = _arquivo_sessao()
    if not os.path.exists(caminho):
        return False
    try:
        with open(caminho) as f:
            dados = json.load(f)
        return bool(dados.get("pin_hash"))
    except Exception:
        return False


def entrar_com_pin(pin):
    global _access_token, _refresh_token, _user_email
    caminho = _arquivo_sessao()
    if not os.path.exists(caminho):
        raise ApiError("Nenhum PIN configurado neste aparelho.")
    try:
        with open(caminho) as f:
            dados = json.load(f)
    except Exception:
        raise ApiError("Não foi possível ler o PIN salvo.")

    if hashlib.sha256(pin.encode()).hexdigest() != dados.get("pin_hash"):
        raise ApiError("PIN incorreto.")

    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token",
            json={"refresh_token": dados["refresh_token"]},
            headers=_headers(autenticado=False),
            timeout=20,
        )
    except requests.RequestException:
        raise ApiError("Não foi possível conectar. Verifique sua internet.")

    resposta = r.json() if r.text else {}
    if r.status_code >= 400:
        raise ApiError("Sessão expirada. Entre novamente com e-mail e senha.")

    _access_token = resposta["access_token"]
    _refresh_token = resposta.get("refresh_token", dados["refresh_token"])
    _user_email = dados["email"]

    dados["refresh_token"] = _refresh_token
    with open(caminho, "w") as f:
        json.dump(dados, f)


def trocar_senha(nova_senha):
    try:
        r = requests.put(
            f"{SUPABASE_URL}/auth/v1/user",
            json={"password": nova_senha},
            headers=_headers(),
            timeout=20,
        )
    except requests.RequestException:
        raise ApiError("Não foi possível conectar. Verifique sua internet.")
    if r.status_code >= 400:
        raise ApiError(_erro_de(r))


def remover_pin():
    caminho = _arquivo_sessao()
    if os.path.exists(caminho):
        os.remove(caminho)


def resgatar_bonus_diario():
    return _rpc("resgatar_bonus_diario", {})


def extrato(conta_id, limite=100):
    return _get("transacoes", params={
        "conta_id": f"eq.{conta_id}",
        "select": "*",
        "order": "id.desc",
        "limit": limite,
    })
