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

def buscar_licoes_aprendidas(supabase: Client):
    """
    Busca as últimas 5 lições aprendidas de previsões que resultaram em 'red'.
    """
    if not supabase:
        return []

    try:
        response = supabase.table('previsoes') \
            .select('licao_aprendida') \
            .eq('status', 'red') \
            .not_('licao_aprendida', 'is', 'null') \
            .order('created_at', desc=True) \
            .limit(5) \
            .execute()

        if hasattr(response, 'data') and response.data:
            # Extrair apenas os textos que não estão vazios
            licoes = [item['licao_aprendida'] for item in response.data if item.get('licao_aprendida') and item['licao_aprendida'].strip() != ""]
            return licoes

        return []
    except Exception as e:
        print(f"Erro ao buscar lições aprendidas: {e}")
        return []
