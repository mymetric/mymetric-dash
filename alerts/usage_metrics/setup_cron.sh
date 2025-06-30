#!/bin/bash

# Script para configurar o cron job do alerta diário do hub
# Execute este script para configurar o envio automático diário

echo "🚀 Configurando Cron Job para Alertas Diários do MyMetric Hub"
echo "=============================================================="

# Obter o diretório atual do projeto
PROJECT_DIR=$(pwd)
echo "📁 Diretório do projeto: $PROJECT_DIR"

# Verificar se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale o Python3 primeiro."
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Verificar se os arquivos necessários existem
if [ ! -f "alerts/usage_metrics/send_daily_hub_alert.py" ]; then
    echo "❌ Arquivo send_daily_hub_alert.py não encontrado!"
    exit 1
fi

if [ ! -f "alerts/usage_metrics/hub_daily_usage.py" ]; then
    echo "❌ Arquivo hub_daily_usage.py não encontrado!"
    exit 1
fi

echo "✅ Arquivos necessários encontrados"

# Verificar se o arquivo de configuração existe
if [ ! -f "alerts/usage_metrics/alert_config.json" ]; then
    echo "⚠️ Arquivo de configuração não encontrado. Criando..."
    PYTHONPATH=. python3 alerts/usage_metrics/send_daily_hub_alert.py config
fi

echo "✅ Configuração verificada"

# Perguntar sobre o horário de envio
echo ""
echo "⏰ Configuração do Horário de Envio"
echo "=================================="
echo "1. 18:00 (recomendado)"
echo "2. 19:00"
echo "3. 20:00"
echo "4. Personalizado"
echo ""
read -p "Escolha o horário (1-4): " time_choice

case $time_choice in
    1)
        HOUR=18
        MINUTE=0
        ;;
    2)
        HOUR=19
        MINUTE=0
        ;;
    3)
        HOUR=20
        MINUTE=0
        ;;
    4)
        read -p "Digite a hora (0-23): " HOUR
        read -p "Digite o minuto (0-59): " MINUTE
        ;;
    *)
        echo "❌ Opção inválida. Usando 18:00 como padrão."
        HOUR=18
        MINUTE=0
        ;;
esac

echo "✅ Horário configurado: $HOUR:$MINUTE"

# Criar o comando do cron
CRON_COMMAND="$MINUTE $HOUR * * * cd $PROJECT_DIR && PYTHONPATH=. python3 alerts/usage_metrics/send_daily_hub_alert.py"

echo ""
echo "📋 Comando do Cron Job:"
echo "$CRON_COMMAND"
echo ""

# Perguntar se deseja adicionar ao crontab
read -p "Deseja adicionar este comando ao crontab? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    # Verificar se já existe um cron job para este script
    if crontab -l 2>/dev/null | grep -q "send_daily_hub_alert.py"; then
        echo "⚠️ Já existe um cron job para este script. Removendo o anterior..."
        crontab -l 2>/dev/null | grep -v "send_daily_hub_alert.py" | crontab -
    fi
    
    # Adicionar novo cron job
    (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron job adicionado com sucesso!"
        echo ""
        echo "📋 Cron jobs ativos:"
        crontab -l
    else
        echo "❌ Erro ao adicionar cron job"
        exit 1
    fi
else
    echo "ℹ️ Cron job não foi adicionado."
    echo "Para adicionar manualmente, execute:"
    echo "crontab -e"
    echo "E adicione a linha:"
    echo "$CRON_COMMAND"
fi

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "📝 Próximos passos:"
echo "1. Edite o arquivo alerts/usage_metrics/alert_config.json com os números corretos"
echo "2. Teste o sistema com: PYTHONPATH=. python3 alerts/usage_metrics/send_daily_hub_alert.py test"
echo "3. O primeiro alerta será enviado automaticamente às $HOUR:$MINUTE"
echo ""
echo "📞 Para suporte, consulte o arquivo alerts/usage_metrics/ALERTAS_README.md" 