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

def buscar_previsao_por_id(supabase: Client, id: str):
    """
    Busca uma previsão específica pelo ID.
    """
    if not supabase:
        return None

    try:
        response = supabase.table('previsoes').select('*').eq('id', id).execute()
        if hasattr(response, 'data') and response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar previsão {id}: {e}")
        return None

def atualizar_previsao(supabase: Client, id: str, dados_atualizacao: dict):
    """
    Atualiza uma previsão com os novos dados (resultado, status, lição).
    """
    if not supabase:
        return False

    try:
        response = supabase.table('previsoes').update(dados_atualizacao).eq('id', id).execute()
        if hasattr(response, 'data') and response.data:
            return True
        return False
    except Exception as e:
        print(f"Erro ao atualizar previsão {id}: {e}")
        return False

def buscar_estatisticas(supabase: Client):
    """
    Busca as estatísticas gerais (Win Rate e Lições na Memória)
    """
    if not supabase:
        return {"win_rate": "0%", "licoes_memoria": 0, "total_greens": 0, "total_reds": 0}

    try:
        # Busca lições
        response_licoes = supabase.table('previsoes') \
            .select('id', count='exact') \
            .not_('licao_aprendida', 'is', 'null') \
            .execute()

        licoes_memoria = response_licoes.count if hasattr(response_licoes, 'count') and response_licoes.count is not None else 0

        # Busca Greens
        response_greens = supabase.table('previsoes') \
            .select('id', count='exact') \
            .eq('status', 'green') \
            .execute()
        total_greens = response_greens.count if hasattr(response_greens, 'count') and response_greens.count is not None else 0

        # Busca Reds
        response_reds = supabase.table('previsoes') \
            .select('id', count='exact') \
            .eq('status', 'red') \
            .execute()
        total_reds = response_reds.count if hasattr(response_reds, 'count') and response_reds.count is not None else 0

        total_fechados = total_greens + total_reds
        win_rate = 0
        if total_fechados > 0:
            win_rate = (total_greens / total_fechados) * 100

        return {
            "win_rate": f"{win_rate:.1f}%",
            "licoes_memoria": licoes_memoria,
            "total_greens": total_greens,
            "total_reds": total_reds,
            "total_jogos": total_fechados
        }
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        return {"win_rate": "0%", "licoes_memoria": 0, "total_greens": 0, "total_reds": 0}
