"""
Script de verificação do ambiente.
Verifica se todas as dependências e configurações estão corretas.
"""
import sys
import os


def check_python_version():
    """Verifica a versão do Python."""
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}", end=" ")
    
    if version.major >= 3 and version.minor >= 9:
        print("OK")
        return True
    else:
        print("ERRO (requer 3.9+)")
        return False


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    required_packages = [
        "streamlit",
        "langchain",
        "langchain_openai",
        "langgraph",
        "pandas",
        "plotly",
        "dotenv"
    ]
    
    all_ok = True
    print("\nDependências:")
    
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package.replace("-", "_"))
            print(f"   {package:20s} OK")
        except ImportError:
            print(f"   {package:20s} FALTANDO")
            all_ok = False
    
    return all_ok


def check_env_file():
    """Verifica o arquivo .env."""
    print("\nArquivo .env:")
    
    if not os.path.exists(".env"):
        print("   ERRO: Arquivo .env não encontrado")
        print("   Dica: Copie .env.example para .env e configure sua API key")
        return False
    
    print("   OK: Arquivo .env encontrado")
    
    # Carregar e verificar API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("   ERRO: OPENAI_API_KEY não configurada")
        print("   Dica: Adicione OPENAI_API_KEY=sua-chave ao arquivo .env")
        return False
    
    if api_key == "sua_chave_api_aqui":
        print("   AVISO: OPENAI_API_KEY ainda é o valor padrão")
        print("   Dica: Substitua pela sua chave real da OpenAI")
        return False
    
    print(f"   OK: OPENAI_API_KEY configurada ({api_key[:10]}...)")
    return True


def check_database():
    """Verifica o banco de dados."""
    print("\nBanco de dados:")
    
    if not os.path.exists("anexo_desafio_1.db"):
        print("   ERRO: Banco de dados não encontrado: anexo_desafio_1.db")
        return False
    
    print("   OK: Banco de dados encontrado")
    
    # Tentar conectar
    try:
        import sqlite3
        conn = sqlite3.connect("anexo_desafio_1.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"   OK: Banco acessível ({len(tables)} tabelas)")
        return True
    except Exception as e:
        print(f"   ERRO: Erro ao acessar banco: {e}")
        return False


def check_structure():
    """Verifica a estrutura de arquivos."""
    print("\nEstrutura do projeto:")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "src/agents/sql_agent.py",
        "src/utils/database.py",
        "src/utils/visualizations.py"
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   {file:40s} OK")
        else:
            print(f"   {file:40s} FALTANDO")
            all_ok = False
    
    return all_ok


def main():
    """Função principal."""
    print("=" * 70)
    print("VERIFICAÇÃO DO AMBIENTE")
    print("=" * 70)
    
    checks = [
        ("Python", check_python_version),
        ("Dependências", check_dependencies),
        ("Configuração", check_env_file),
        ("Banco de Dados", check_database),
        ("Estrutura", check_structure)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"\nErro ao verificar {name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    
    if all(results):
        print("TUDO OK! Sistema pronto para uso.")
        print("\nExecute: streamlit run app.py")
    else:
        print("ALGUNS PROBLEMAS ENCONTRADOS")
        print("\nConsulte o INSTALL.md para instruções detalhadas")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
