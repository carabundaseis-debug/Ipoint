# Comandos do Termux — Ipoint

Comandos prontos com o seu repositório (`carabundaseis-debug/Ipoint`).

---

## Atualizar o projeto (substitui TUDO pela versão mais nova)

Isso sobrescreve todos os arquivos do projeto na pasta local, sem mexer no
`.git` (então não precisa refazer o `remote add` nem nada relacionado ao
GitHub em si):

```bash
cd ~/storage/downloads
unzip -o ipoint.zip -d ipoint
cd ipoint
git add -A
git commit -m "Atualizacao do projeto"
git push
```

Se em algum momento o `git push` for recusado (rejected / non-fast-forward),
use:

```bash
git push --force
```

---

## Primeiro envio (só se for a primeira vez, repositório ainda vazio)

```bash
pkg update -y
pkg install git -y
termux-setup-storage

cd ~/storage/downloads
unzip ipoint.zip -d ipoint
cd ipoint
git init
git add .
git commit -m "Primeiro envio do Ipoint"
git branch -M main
git remote add origin https://github.com/carabundaseis-debug/Ipoint.git
git push -u origin main
```

Usuário: seu usuário do GitHub. "Senha": o token de acesso pessoal (`ghp_...`).

---

## Acompanhar o build

```
https://github.com/carabundaseis-debug/Ipoint/actions
```

Espera o ✅ verde (ou ❌ vermelho). Se falhar, baixa o artefato
**`build-log-resumo`** (é pequeno, só as últimas 400 linhas do log) e manda
o conteúdo pro Claude.

---

## Dica

Se der erro de "dubious ownership" no git:

```bash
git config --global --add safe.directory /storage/emulated/0/Download/ipoint
```
