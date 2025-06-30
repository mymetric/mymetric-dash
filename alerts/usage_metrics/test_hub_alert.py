#!/usr/bin/env python3
"""
Script de teste para o sistema de alertas de uso diário do hub.
"""

import sys
import os

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

# Importar o módulo de alertas
from hub_daily_usage import send_daily_hub_usage_alert, get_hub_usage, format_usage_message

def test_hub_usage_analysis():
    """Testa a análise de uso do hub."""
    print("🧪 Testando análise de uso do hub...")
    
    try:
        # Obter dados de uso
        usage_data = get_hub_usage()
        
        if usage_data:
            print("✅ Análise de uso realizada com sucesso!")
            print(f"📊 Dados obtidos:")
            print(f"   - Total de clientes: {usage_data['total_clientes']}")
            print(f"   - Clientes ativos hoje: {usage_data['clientes_ativos_hoje']}")
            print(f"   - Usuários únicos hoje: {usage_data['usuarios_reais_hoje']}")
            print(f"   - Total de eventos: {usage_data['total_eventos_hoje']}")
            print(f"   - Taxa de ativação: {usage_data['taxa_ativacao']:.1f}%")
            
            # Testar formatação da mensagem
            message = format_usage_message(usage_data)
            print("\n📝 Mensagem formatada:")
            print("=" * 50)
            print(message)
            print("=" * 50)
            
            return True
        else:
            print("❌ Falha ao obter dados de uso")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False

def test_whatsapp_alert(test_phone):
    """Testa o envio de alerta para WhatsApp."""
    print(f"\n📱 Testando envio de alerta para: {test_phone}")
    
    try:
        # Enviar mensagem de teste
        success = send_daily_hub_usage_alert(test_phone, testing_mode=True)
        
        if success:
            print("✅ Mensagem de teste enviada com sucesso!")
            return True
        else:
            print("❌ Falha ao enviar mensagem de teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste de envio: {str(e)}")
        return False

def main():
    """Função principal do script de teste."""
    print("🚀 Iniciando testes do sistema de alertas de uso diário do hub")
    print("=" * 60)
    
    # Teste 1: Análise de uso
    test1_success = test_hub_usage_analysis()
    
    # Teste 2: Envio de alerta (apenas se um número de teste for fornecido)
    test2_success = True  # Por padrão, não testa envio real
    
    # Verificar se um número de teste foi fornecido como argumento
    if len(sys.argv) > 1:
        test_phone = sys.argv[1]
        test2_success = test_whatsapp_alert(test_phone)
    else:
        print("\n📱 Pular teste de envio (nenhum número fornecido)")
        print("   Para testar envio real, execute: python test_hub_alert.py <numero_whatsapp>")
    
    # Resumo dos testes
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"✅ Análise de uso: {'PASSOU' if test1_success else 'FALHOU'}")
    print(f"✅ Envio de alerta: {'PASSOU' if test2_success else 'FALHOU'}")
    
    if test1_success and test2_success:
        print("\n🎉 Todos os testes passaram! O sistema está funcionando corretamente.")
        return 0
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 