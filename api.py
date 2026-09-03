"""
Cliente da API do Ipoint (Supabase).
Faz login/registro e todas as operações de conta pela internet,
em vez de guardar tudo só no celular.
"""
import requests

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


def transferir_para_email(email_destino, valor, descricao=None):
    _rpc("transferir_para_email", {
        "email_destino": email_destino.strip().lower(),
        "valor_transferido": float(valor),
        "descricao_transferencia": descricao,
    })


def resgatar_bonus_diario():
    return _rpc("resgatar_bonus_diario", {})


def extrato(conta_id, limite=100):
    return _get("transacoes", params={
        "conta_id": f"eq.{conta_id}",
        "select": "*",
        "order": "id.desc",
        "limit": limite,
    })
