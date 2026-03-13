import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Carregar variáveis de ambiente
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Inicializa o cliente do Supabase
def get_supabase_client() -> Client:
    if not url or not key:
        print("Aviso: SUPABASE_URL ou SUPABASE_KEY não configuradas. Banco de dados não será acessível.")
        return None

    return create_client(url, key)
