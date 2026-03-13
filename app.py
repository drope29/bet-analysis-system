from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper import DataScraper
from db import get_supabase_client, buscar_licoes_aprendidas, buscar_previsao_por_id, atualizar_previsao, buscar_estatisticas
from ia import AnalistaIA
from math_utils import calcular_media_ponderada, probabilidade_over_gols
from dotenv import load_dotenv
import json
import re

load_dotenv()

app = Flask(__name__)
CORS(app) # Allow cross-origin requests from Vue frontend
supabase = get_supabase_client()
scraper = DataScraper()
analista = AnalistaIA()

@app.route('/analisar', methods=['POST'])
def analisar_partida():
    data = request.get_json()

    if not data or 'time_casa' not in data or 'time_fora' not in data:
        return jsonify({"erro": "Parâmetros 'time_casa' e 'time_fora' são obrigatórios."}), 400

    time_casa = data['time_casa']
    time_fora = data['time_fora']
    odd_informada = data.get('odd')

    print(f"Iniciando análise para: {time_casa} x {time_fora} com Odd: {odd_informada}")

    # 1. Coletar dados usando o Scraper
    dados_casa = scraper.scrape_team_data(time_casa)
    dados_fora = scraper.scrape_team_data(time_fora)

    dados_brutos = {
        "casa": dados_casa,
        "fora": dados_fora
    }

    # 2. Refinamento Matemático (Médias ponderadas e Poisson)
    # Extrair os arrays de jogos para o calculo
    jogos_casa = dados_casa.get('ultimos_10_jogos', [])
    jogos_fora = dados_fora.get('ultimos_10_jogos', [])

    calculos = {}
    if len(jogos_casa) > 0 and len(jogos_fora) > 0:
        calculos['media_ponderada_escanteios_casa'] = calcular_media_ponderada(jogos_casa, 'escanteios')
        calculos['media_ponderada_escanteios_fora'] = calcular_media_ponderada(jogos_fora, 'escanteios')

        # Média ponderada de gols marcados pelo Time Casa (placar_casa quando joga em casa, placar_fora quando joga fora.
        # Como o scraper ta misturando, vamos usar placar_casa assumindo que seja o time que estamos raspando)
        calculos['media_ponderada_gols_marcados_casa'] = calcular_media_ponderada(jogos_casa, 'placar_casa')

        # Média ponderada de gols sofridos pelo Time Fora
        calculos['media_ponderada_gols_sofridos_fora'] = calcular_media_ponderada(jogos_fora, 'placar_fora')

        calculos['poisson_over_1_5'] = probabilidade_over_gols(
            calculos['media_ponderada_gols_marcados_casa'],
            calculos['media_ponderada_gols_sofridos_fora'],
            over_limit=1.5
        )

    # 3. Buscar lições aprendidas (memória de erros)
    erros_passados = buscar_licoes_aprendidas(supabase)

    # 4. Chamar a IA para gerar a análise estruturada (agora com matemática e odd)
    palpite_ia = analista.analisar(dados_casa, dados_fora, erros_passados, calculos, odd_informada)

    registro = {
        "time_casa": time_casa,
        "time_fora": time_fora,
        "dados_brutos": dados_brutos,
        "palpite_ia": palpite_ia,
        "status": "pendente"
    }

    # 2. Salvar o registro inicial no banco de dados (Supabase)
    if supabase:
        try:
            response = supabase.table('previsoes').insert(registro).execute()
            if hasattr(response, 'data') and len(response.data) > 0:
                return jsonify({
                    "mensagem": "Análise iniciada e salva com sucesso.",
                    "id": response.data[0]['id'],
                    "palpite_ia": palpite_ia
                }), 201
            else:
                return jsonify({"erro": "Erro ao salvar no Supabase.", "detalhe": str(response)}), 500
        except Exception as e:
            return jsonify({"erro": "Exceção ao acessar o Supabase.", "detalhes": str(e)}), 500
    else:
        # Se o Supabase não estiver configurado, retorna sucesso apenas com os dados coletados (modo mock)
        return jsonify({
            "mensagem": "Análise iniciada (modo mock - Supabase não configurado).",
            "palpite_ia": palpite_ia,
            "dados": registro
        }), 200

def avaliar_resultado(palpite_ia, resultado_real):
    """
    Compara o palpite da IA com o resultado real.
    Esta é uma implementação simplificada; na prática, seria necessário
    um parser robusto para entender exatamente o que a IA previu em string.
    """
    status = 'green'

    # Avaliar Vencedor 1x2 (Exemplo simplificado)
    vencedor_real = None
    if resultado_real['placar_casa'] > resultado_real['placar_fora']:
        vencedor_real = "casa"
    elif resultado_real['placar_casa'] < resultado_real['placar_fora']:
        vencedor_real = "fora"
    else:
        vencedor_real = "empate"

    vencedor_ia = str(palpite_ia.get('vencedor_1x2', {}).get('palpite', '')).lower()

    # Verifica se a IA errou de forma grotesca o vencedor/empate
    # Se a IA previu Casa e deu Fora/Empate, é red.
    if ("casa" in vencedor_ia and vencedor_real != "casa") or \
       ("fora" in vencedor_ia and vencedor_real != "fora") or \
       ("empate" in vencedor_ia and vencedor_real != "empate"):
           status = 'red'

    # Poderiamos adicionar lógica similar para Over/Under Gols
    soma_gols = resultado_real['placar_casa'] + resultado_real['placar_fora']
    over_under_ia = str(palpite_ia.get('over_under_gols', {}).get('palpite', '')).lower()

    # Simplificação: se previu Over 2.5 e deu 2 ou menos
    if "over" in over_under_ia and "2.5" in over_under_ia and soma_gols < 3:
        status = 'red'
    elif "under" in over_under_ia and "2.5" in over_under_ia and soma_gols >= 3:
        status = 'red'

    return status

@app.route('/fechar-jogo', methods=['POST'])
def fechar_jogo():
    data = request.get_json()

    if not data or 'id' not in data:
        return jsonify({"erro": "Parâmetro 'id' é obrigatório."}), 400

    id_previsao = data['id']

    # 1. Buscar a previsão original no banco
    if not supabase:
        return jsonify({"erro": "Banco de dados não conectado."}), 500

    previsao = buscar_previsao_por_id(supabase, id_previsao)
    if not previsao:
        return jsonify({"erro": "Previsão não encontrada."}), 404

    if previsao.get('status') != 'pendente':
        return jsonify({"mensagem": f"O jogo já foi fechado com status '{previsao.get('status')}'."}), 400

    time_casa = previsao.get('time_casa')
    time_fora = previsao.get('time_fora')

    print(f"Fechando jogo: {time_casa} x {time_fora}")

    # 2. Buscar o resultado real usando o Scraper (com Retry)
    resultado_real = scraper.scrape_match_result(time_casa, time_fora)

    # 3. Comparar resultado com previsão (Lógica de Green/Red)
    palpite_ia = previsao.get('palpite_ia', {})
    if type(palpite_ia) == str:
        try:
            palpite_ia = json.loads(palpite_ia)
        except:
            pass

    status_final = avaliar_resultado(palpite_ia, resultado_real)
    print(f"Status calculado: {status_final.upper()}")

    licao_aprendida = None

    # 4. Reflexão da IA (O Aprendizado)
    if status_final == 'red':
        print("IA errou o palpite. Iniciando processo de reflexão...")
        dados_brutos = previsao.get('dados_brutos', {})
        if type(dados_brutos) == str:
            try:
                dados_brutos = json.loads(dados_brutos)
            except:
                pass

        licao_aprendida = analista.refletir_erro(dados_brutos, palpite_ia, resultado_real)
        print(f"Lição aprendida gerada: {licao_aprendida[:50]}...")

    # 5. Atualizar o banco de dados
    dados_atualizacao = {
        "resultado_real": resultado_real,
        "status": status_final,
        "licao_aprendida": licao_aprendida
    }

    sucesso = atualizar_previsao(supabase, id_previsao, dados_atualizacao)

    if sucesso:
        return jsonify({
            "mensagem": f"Jogo fechado com sucesso. Status: {status_final.upper()}",
            "resultado_real": resultado_real,
            "licao_aprendida": licao_aprendida
        }), 200
    else:
        return jsonify({"erro": "Erro ao atualizar a previsão no banco de dados."}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Retorna as estatísticas do sistema (Win Rate, Lições Aprendidas)"""
    if not supabase:
        return jsonify({
            "win_rate": "Mocked 65%",
            "licoes_memoria": 42,
            "total_greens": 13,
            "total_reds": 7,
            "total_jogos": 20
        }), 200

    estatisticas = buscar_estatisticas(supabase)
    return jsonify(estatisticas), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
