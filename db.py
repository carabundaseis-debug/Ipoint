"""
Camada de dados do Ipoint.
Usa SQLite local (arquivo no diretório de dados do app) para guardar
contas e o extrato de transações. Todos os valores são guardados com
2 casas decimais (ex: 1.50), nunca inteiros forçados.
"""
import sqlite3
import os
from datetime import datetime

try:
    from kivy.app import App
except ImportError:
    App = None


def get_db_path():
    """Retorna o caminho do arquivo do banco, dentro da pasta de dados do app."""
    if App is not None and App.get_running_app() is not None:
        base = App.get_running_app().user_data_dir
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "ipoint.db")


def get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            saldo REAL NOT NULL DEFAULT 0,
            criada_em TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,          -- 'entrada' ou 'saida'
            valor REAL NOT NULL,
            descricao TEXT,
            data TEXT NOT NULL,
            FOREIGN KEY (conta_id) REFERENCES contas (id)
        )
    """)
    conn.commit()

    # Garante que sempre existe pelo menos uma conta principal
    cur.execute("SELECT COUNT(*) as c FROM contas")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO contas (nome, saldo, criada_em) VALUES (?, ?, ?)",
            ("Minha Conta", 0.0, datetime.now().isoformat()),
        )
        conn.commit()
    conn.close()


def listar_contas():
    conn = get_conn()
    contas = conn.execute("SELECT * FROM contas ORDER BY id").fetchall()
    conn.close()
    return contas


def obter_conta(conta_id):
    conn = get_conn()
    conta = conn.execute("SELECT * FROM contas WHERE id = ?", (conta_id,)).fetchone()
    conn.close()
    return conta


def criar_conta(nome, saldo_inicial=0.0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contas (nome, saldo, criada_em) VALUES (?, ?, ?)",
        (nome.strip(), round(float(saldo_inicial), 2), datetime.now().isoformat()),
    )
    conta_id = cur.lastrowid
    if saldo_inicial and float(saldo_inicial) != 0:
        _registrar_transacao(cur, conta_id, "entrada", float(saldo_inicial), "Saldo inicial")
    conn.commit()
    conn.close()
    return conta_id


def renomear_conta(conta_id, novo_nome):
    conn = get_conn()
    conn.execute("UPDATE contas SET nome = ? WHERE id = ?", (novo_nome.strip(), conta_id))
    conn.commit()
    conn.close()


def excluir_conta(conta_id):
    conn = get_conn()
    conn.execute("DELETE FROM transacoes WHERE conta_id = ?", (conta_id,))
    conn.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
    conn.commit()
    conn.close()


def _registrar_transacao(cur, conta_id, tipo, valor, descricao):
    cur.execute(
        "INSERT INTO transacoes (conta_id, tipo, valor, descricao, data) VALUES (?, ?, ?, ?, ?)",
        (conta_id, tipo, round(float(valor), 2), descricao, datetime.now().isoformat()),
    )


def depositar(conta_id, valor, descricao="Depósito"):
    """Adiciona pontos a uma conta (simulando um crédito/depósito manual)."""
    valor = round(float(valor), 2)
    if valor <= 0:
        raise ValueError("O valor precisa ser maior que zero.")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE contas SET saldo = saldo + ? WHERE id = ?", (valor, conta_id))
    _registrar_transacao(cur, conta_id, "entrada", valor, descricao)
    conn.commit()
    conn.close()


def transferir(origem_id, destino_id, valor, descricao=""):
    """Transfere pontos entre duas contas, com checagem de saldo."""
    if origem_id == destino_id:
        raise ValueError("A conta de origem e destino não podem ser a mesma.")
    valor = round(float(valor), 2)
    if valor <= 0:
        raise ValueError("O valor precisa ser maior que zero.")

    conn = get_conn()
    cur = conn.cursor()
    origem = cur.execute("SELECT * FROM contas WHERE id = ?", (origem_id,)).fetchone()
    if origem is None:
        conn.close()
        raise ValueError("Conta de origem não encontrada.")
    if origem["saldo"] < valor:
        conn.close()
        raise ValueError("Saldo insuficiente para essa transferência.")

    destino = cur.execute("SELECT * FROM contas WHERE id = ?", (destino_id,)).fetchone()
    if destino is None:
        conn.close()
        raise ValueError("Conta de destino não encontrada.")

    cur.execute("UPDATE contas SET saldo = saldo - ? WHERE id = ?", (valor, origem_id))
    cur.execute("UPDATE contas SET saldo = saldo + ? WHERE id = ?", (valor, destino_id))

    desc_saida = descricao or f"Transferência para {destino['nome']}"
    desc_entrada = descricao or f"Transferência de {origem['nome']}"
    _registrar_transacao(cur, origem_id, "saida", valor, desc_saida)
    _registrar_transacao(cur, destino_id, "entrada", valor, desc_entrada)

    conn.commit()
    conn.close()


def extrato(conta_id, limite=100):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM transacoes WHERE conta_id = ? ORDER BY id DESC LIMIT ?",
        (conta_id, limite),
    ).fetchall()
    conn.close()
    return rows
