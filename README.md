# Ipoint

Um "banco" — só que em vez de dinheiro, o saldo é em **pontos** (aceita casas
decimais, tipo 1,50). Dá pra criar várias contas, transferir pontos entre
elas, depositar e ver o extrato. Tema azul escuro + ciano.

Como o Termux **não consegue compilar um `.apk` sozinho** (falta SDK/NDK do
Android), o projeto já vem com um robô configurado (GitHub Actions) que
compila o app pra você, na nuvem, toda vez que você enviar o código pro
GitHub. Você só usa o Termux pra mandar os arquivos.

## Passo 1 — Criar o repositório no GitHub

1. No site ou app do GitHub, crie um repositório novo (ex: `pontos-app`).
   Pode deixar público ou privado, os dois funcionam.
2. Não precisa adicionar nada nele (README, .gitignore) — vai ficar vazio.

## Passo 2 — Preparar o Termux

Se ainda não tiver o `git` instalado:

```bash
pkg update -y
pkg install git -y
```

## Passo 3 — Extrair o zip e enviar pro GitHub

1. Baixe o `pontos-app.zip` que eu te mandei e coloque na pasta de Downloads
   do celular.
2. No Termux, dê acesso ao armazenamento (só na primeira vez):
   ```bash
   termux-setup-storage
   ```
3. Vá até a pasta de Downloads e extraia o zip:
   ```bash
   cd ~/storage/downloads
   unzip pontos-app.zip -d pontos-app
   cd pontos-app
   ```
4. Conecte esse projeto ao repositório que você criou (troque a URL pela do
   seu repositório):
   ```bash
   git init
   git add .
   git commit -m "Primeiro envio do Ipoint"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/pontos-app.git
   git push -u origin main
   ```
   O GitHub vai pedir seu usuário e uma **senha de acesso pessoal (token)**
   — não é a senha normal da conta. Se precisar, me avise que te explico
   como gerar esse token.

## Passo 4 — Acompanhar a compilação do APK

1. Abra o repositório no site do GitHub, pelo navegador do celular.
2. Vá na aba **Actions**. Você vai ver o workflow "Build APK" rodando
   (leva uns 15-25 minutos na primeira vez, porque baixa o Android SDK/NDK
   — nas próximas fica mais rápido).
3. Quando terminar com um ✅ verde, clique nele, desça até **Artifacts** e
   baixe o `ipoint-apk`.
4. Isso baixa um `.zip` — dentro dele está o `.apk` de verdade.

## Passo 5 — Instalar no celular

1. Extraia o `.apk` do zip baixado (o próprio app de Arquivos do Android
   faz isso).
2. Toque no `.apk` pra instalar. Se aparecer aviso de "fonte desconhecida",
   é normal — permita a instalação (Configurações > Segurança > Instalar
   apps desconhecidos, autorizando o navegador ou o app de Arquivos).

## Enviando atualizações depois

Sempre que eu te mandar um zip novo com melhorias, o fluxo é:

```bash
cd ~/storage/downloads
unzip -o pontos-app-v2.zip -d pontos-app_novo
cd pontos-app_novo
git init
git remote add origin https://github.com/SEU_USUARIO/pontos-app.git
git add .
git commit -m "Atualização"
git branch -M main
git push -u origin main --force
```

E repete o Passo 4 pra pegar o novo APK.

## Estrutura do projeto

- `main.py` — telas e visual do app (Kivy)
- `db.py` — toda a lógica de contas, saldo e transferências (SQLite local)
- `icon.png` — ícone do app (aparece na tela inicial do Android)
- `buildozer.spec` — configuração de como o app é empacotado pro Android
- `.github/workflows/build.yml` — robô que compila o APK automaticamente

## Ideias pra próximas versões

- PIN/senha pra abrir o app
- Editar/excluir conta
- Gráfico de saldo ao longo do tempo
- Categorias nas transações
