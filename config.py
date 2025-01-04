# Configurações gerais
CONNECT_RATE_THRESHOLD = 80.0
COOKIE_LOSS_THRESHOLD = 20.0

# Cores
CHART_COLORS = {
    'sessions': '#D1B1C8',
    'revenue': '#C5EBC3'
}

# Discord
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."

# Métricas
METRICS_CONFIG = {
    'sessions': {'label': 'Sessões', 'format': '{:,}'},
    'orders': {'label': 'Pedidos', 'format': '{:,}'},
    'revenue': {'label': 'Receita', 'format': 'R$ {:,.2f}'}
} 