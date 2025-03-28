import random

QUOTES = [
    # Análise de Dados
    "Sem dados, você é apenas mais uma pessoa com uma opinião.",
    "Dados bem analisados falam por si.",
    "A análise começa com a curiosidade.",
    "Dados não mentem, mas também não contam toda a história.",
    "A estatística é o coração da análise de dados.",
    "Uma boa pergunta vale mais que mil dashboards.",
    "Decisão baseada em dados é decisão com direção.",
    "Dados revelam padrões, não certezas.",
    "Encontrar o insight certo é como achar ouro num rio de números.",
    "A beleza da análise está em transformar complexidade em clareza.",
    
    # Ciência de Dados
    "Ciência de dados é onde matemática encontra propósito.",
    "O cientista de dados é o contador de histórias do século XXI.",
    "Dados + algoritmo + contexto = insight.",
    "Modelos preditivos são mapas, não GPS.",
    "A ciência de dados transforma intuição em evidência.",
    
    # Visualização de Dados
    "Um gráfico vale mais que mil tabelas.",
    "Boa visualização é clareza, não decoração.",
    "Dados são o quê; visualizações são o como.",
    "Um gráfico mal feito pode esconder uma verdade.",
    "A melhor visualização é aquela que comunica com simplicidade.",
    
    # Big Data
    "Big Data sem propósito é só um grande gasto.",
    "Volume não é valor — insight é.",
    "Nem todo dado é útil. Nem todo Big Data é inteligente.",
    "Não precisamos de mais dados, precisamos dos dados certos.",
    "Big Data exige Big Responsabilidade.",
    
    # Privacidade e Ética
    "Dado pessoal não é só número — é dignidade.",
    "Com grandes dados vêm grandes responsabilidades.",
    "Ética é o algoritmo invisível da análise.",
    "Privacidade não deve ser opcional.",
    "Anonimizar não é esquecer a responsabilidade.",
    
    # Técnicas e Práticas
    "Garbage in, garbage out.",
    "Limpeza de dados é 80% do trabalho — e 90% do estresse.",
    "Dado estruturado é um privilégio.",
    "SQL é poesia para quem ama dados.",
    "API é a ponte entre sistemas e insights.",
    
    # Cultura Data-Driven
    "Cultura orientada a dados é mais sobre pessoas que sobre tecnologia.",
    "Uma empresa data-driven toma decisões, não apostas.",
    "Sem confiança nos dados, não há confiança nas decisões.",
    "Quem domina os dados, lidera o mercado.",
    "Dados são ativos estratégicos — trate-os como tal.",
    
    # Bem-humoradas
    "'Funciona no Excel' não é um elogio.",
    "O dado some. O backup, também.",
    "Debug de dados: onde a realidade encontra a ficção.",
    "Nada como um join errado para estragar sua tarde.",
    "Toda sexta-feira é dia de descobrir um bug nos dados.",
    
    # Inspiradoras
    "Dados não mudam o mundo — pessoas com dados mudam.",
    "Informação é poder. Dados bem usados são superpoder.",
    "Grandes descobertas começam com pequenas observações.",
    "A intuição leva ao dado. O dado valida a intuição.",
    "A curiosidade é o motor da análise.",
    
    # Práticas e Diretas
    "Se você não mede, não melhora.",
    "Métrica sem contexto é ruído.",
    "Métricas diferentes contam verdades diferentes.",
    "Um KPI mal definido destrói uma estratégia.",
    "O relatório perfeito é o que responde antes da pergunta."
]

def get_random_quote():
    """Retorna uma citação aleatória sobre análise de dados."""
    return random.choice(QUOTES) 