from flask import Flask, request, jsonify
from scraper import DataScraper
from db import get_supabase_client, buscar_licoes_aprendidas
from ia import AnalistaIA
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
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

    print(f"Iniciando análise para: {time_casa} x {time_fora}")

    # 1. Coletar dados usando o Scraper
    dados_casa = scraper.scrape_team_data(time_casa)
    dados_fora = scraper.scrape_team_data(time_fora)

    dados_brutos = {
        "casa": dados_casa,
        "fora": dados_fora
    }

    # 2. Buscar lições aprendidas (memória de erros)
    erros_passados = buscar_licoes_aprendidas(supabase)

    # 3. Chamar a IA para gerar a análise estruturada
    palpite_ia = analista.analisar(dados_casa, dados_fora, erros_passados)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
