-- Cria o dataset de configuração se não existir
CREATE SCHEMA IF NOT EXISTS `mymetric-hub-shopify.dbt_config`;

-- Cria a tabela de avisos dos usuários
CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.user_notices` (
    username STRING NOT NULL,
    notices STRING,  -- JSON com os avisos fechados
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY(username) NOT ENFORCED
);

-- Cria a tabela de metas dos usuários
CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.user_goals` (
    username STRING NOT NULL,
    goals STRING,  -- JSON com as metas
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY(username) NOT ENFORCED
);

-- Cria a tabela de configurações gerais dos usuários
CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.user_settings` (
    username STRING NOT NULL,
    settings STRING,  -- JSON com as configurações
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY(username) NOT ENFORCED
);

-- Cria a tabela de eventos de usuário
CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.user_events` (
    username STRING,
    event_type STRING,
    event_data STRING,  -- JSON com os dados do evento
    created_at TIMESTAMP
); 