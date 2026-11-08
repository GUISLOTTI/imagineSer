#!/usr/bin/env bash
# Hook PreToolUse do Claude Code para comandos Bash e PowerShell.
# Recebe o JSON da chamada na entrada padrão. Sair com código 2 bloqueia a chamada
# e devolve a mensagem de stderr ao Claude. Sem dependências (não usa jq).
# Confirme o formato do JSON e o comportamento do código 2 em https://code.claude.com/docs/en/hooks

entrada="$(cat)"

bloquear() {
  echo "BLOQUEADO pelo hook do projeto: $1" >&2
  exit 2
}

# 1. Ler ou exibir segredos
if echo "$entrada" | grep -Eq '(cat|less|more|head|tail|type|grep|sed|awk|Get-Content|\bgc\b|Select-String|Copy-Item)[^"]*\.env'; then
  bloquear "leitura de arquivo .env não é permitida."
fi
if echo "$entrada" | grep -Eq '(printenv|env\b|set\b).*(TOKEN|KEY|SECRET)'; then
  bloquear "exibir variáveis de segredo não é permitido."
fi

# 2. Publicar fora do workflow
if echo "$entrada" | grep -Eq 'Factory\.Cli[^"]*publicar|factory[^"]*publicar'; then
  bloquear "o comando publicar só roda no workflow 'publicar' do GitHub Actions."
fi

# 3. Chamadas diretas à API do Buffer
if echo "$entrada" | grep -Eq 'api\.buffer\.com'; then
  bloquear "chamadas ao Buffer só pela Factory.Cli nos workflows 'publicar' e 'reconciliar'."
fi

exit 0
