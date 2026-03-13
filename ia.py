import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configurar a API do Gemini
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

class AnalistaIA:
    def __init__(self):
        # Instrução do sistema conforme solicitado
        self.system_instruction = (
            "Você é um analista estatístico de apostas. "
            "Analise probabilidade de Vitória/Empate, Over/Under Gols, Escanteios, Cartões e Chutes ao Gol. "
            "Use os dados brutos para justificar cada palpite."
        )

        # Como o pacote google-generativeai evoluiu, para usar system instructions podemos usar o modelo Gemini 1.5 Pro ou Flash.
        # Caso o usuário não tenha o 1.5, faremos um fallback para adicionar a system instruction no prompt
        try:
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=self.system_instruction,
                generation_config={"response_mime_type": "application/json"}
            )
        except Exception as e:
            print(f"Aviso: Falha ao inicializar o modelo com system_instruction nativo. Detalhes: {e}")
            self.model = None

    def analisar(self, dados_casa, dados_fora, erros_passados=None, calculos_matematicos=None, odd_informada=None):
        """
        Envia os dados e os cálculos matemáticos para o Gemini e retorna a análise estruturada em JSON.
        """
        if not gemini_api_key:
            print("Aviso: GEMINI_API_KEY não configurada. Retornando palpite simulado.")
            return self._gerar_palpite_simulado(dados_casa, dados_fora, calculos_matematicos)

        # Se falhou a inicialização do modelo (ex: versão incompatível do SDK ou key inválida pro modelo)
        if not self.model:
            self.model = genai.GenerativeModel("gemini-pro") # Fallback pro modelo antigo sem json mode nativo

        # Preparar o prompt com a memória de erros
        prompt_erros = ""
        if erros_passados and len(erros_passados) > 0:
            lista_erros = "\n".join([f"- {erro}" for erro in erros_passados])
            prompt_erros = f"\n\nEvite os seguintes erros cometidos em análises passadas:\n{lista_erros}"

        prompt_matematico = ""
        if calculos_matematicos:
            prompt_matematico = (
                f"\n\nProvas Sociais (Cálculos Matemáticos Rigorosos):\n"
                f"- A média ponderada temporal de escanteios do Time Casa é {calculos_matematicos.get('media_ponderada_escanteios_casa', 0):.1f} e do Time Fora é {calculos_matematicos.get('media_ponderada_escanteios_fora', 0):.1f}.\n"
                f"- A média ponderada temporal de gols marcados pelo Time Casa é {calculos_matematicos.get('media_ponderada_gols_marcados_casa', 0):.1f}.\n"
                f"- A média ponderada temporal de gols sofridos pelo Time Fora é {calculos_matematicos.get('media_ponderada_gols_sofridos_fora', 0):.1f}.\n"
                f"- A probabilidade de Poisson para Over 1.5 gols no jogo é {calculos_matematicos.get('poisson_over_1_5', 0):.1f}%.\n"
                f"Use esses números como prova social para sua análise final.\n"
            )

        prompt_ev = ""
        if odd_informada:
            prompt_ev = (
                f"\n\nCálculo de Valor Esperado (EV+):\n"
                f"A Odd oferecida pela casa de aposta é {odd_informada}.\n"
                f"Implemente a seguinte lógica no seu json de retorno APENAS para o mercado principal (vencedor_1x2):\n"
                f"1. Defina a 'Probabilidade Real' como a média entre sua própria 'Cálculo IA' e os 'Cálculos Matemáticos' (poisson/ponderada).\n"
                f"2. Calcule o Valor Esperado: EV = (Probabilidade Real (em decimal) * Odd) - 1.\n"
                f"3. O sistema só deve recomendar o 'Green' se o Valor Esperado for maior que 0.15 (margem de segurança de 15%).\n"
                f"4. Adicione um campo booleano 'alta_convergencia' em cada mercado. Deve ser true se a análise IA convergir com a matemática e o EV (se aplicável) for > 0.15.\n"
            )

        prompt = (
            f"Dados do Time da Casa ({dados_casa.get('time', 'Casa')}): {json.dumps(dados_casa.get('ultimos_10_jogos', []))}\n\n"
            f"Dados do Time de Fora ({dados_fora.get('time', 'Fora')}): {json.dumps(dados_fora.get('ultimos_10_jogos', []))}\n\n"
            f"Gere uma análise estruturada contendo as porcentagens de confiança e justificativas para os mercados: "
            f"Vencedor (1x2), Over/Under Gols, Escanteios, Cartões e Chutes ao Gol."
            f"{prompt_matematico}"
            f"{prompt_ev}"
            f"{prompt_erros}"
            f"\n\nLembre-se de retornar UM OBJETO JSON onde cada mercado possui 'palpite', 'confianca', 'justificativa' e 'alta_convergencia' (booleano)."
        )

        # Se usarmos o gemini-pro antigo, precisamos forçar que ele responda em JSON pelo texto
        if self.model.model_name == "models/gemini-pro":
             prompt = self.system_instruction + "\n\nResponda APENAS com um objeto JSON válido.\n" + prompt

        try:
            print("Enviando dados para o Gemini...")
            response = self.model.generate_content(prompt)
            texto_resposta = response.text

            # Limpar formatações de markdown se houver (ex: ```json ... ```)
            if texto_resposta.startswith("```json"):
                texto_resposta = texto_resposta[7:-3].strip()
            elif texto_resposta.startswith("```"):
                texto_resposta = texto_resposta[3:-3].strip()

            resultado_json = json.loads(texto_resposta)
            return resultado_json
        except Exception as e:
            print(f"Erro ao chamar a API do Gemini: {e}")
            return self._gerar_palpite_simulado(dados_casa, dados_fora)

    def _gerar_palpite_simulado(self, dados_casa, dados_fora, calculos_matematicos=None):
        # Mock do retorno da IA para caso a API falhe ou a chave não exista
        time_casa = dados_casa.get("time", "Casa")
        time_fora = dados_fora.get("time", "Fora")

        # Simula a prova social
        alta_conv = False
        if calculos_matematicos and calculos_matematicos.get('poisson_over_1_5', 0) > 70:
            alta_conv = True

        return {
            "vencedor_1x2": {
                "palpite": time_casa,
                "confianca": "86%",
                "justificativa": f"Simulação: {time_casa} tem alta convergência matemática.",
                "alta_convergencia": alta_conv
            },
            "over_under_gols": {
                "palpite": "Over 1.5",
                "confianca": "90%",
                "justificativa": "Poisson e IA indicam alta probabilidade de gols.",
                "alta_convergencia": alta_conv
            },
            "escanteios": {
                "palpite": "Over 8.5",
                "confianca": "80%",
                "justificativa": "Média ponderada alta nos últimos 3 jogos.",
                "alta_convergencia": False
            },
            "cartoes": {
                "palpite": "Under 4.5",
                "confianca": "60%",
                "justificativa": "Ambos os times simulam poucas faltas.",
                "alta_convergencia": False
            },
            "chutes_ao_gol": {
                "palpite": "Casa Over 4.5",
                "confianca": "55%",
                "justificativa": "Agressividade nas finalizações dentro de casa.",
                "alta_convergencia": False
            }
        }

    def refletir_erro(self, dados_brutos, palpite_ia, resultado_real):
        """
        Gera uma lição aprendida quando a IA erra uma previsão.
        """
        if not gemini_api_key:
            print("Aviso: GEMINI_API_KEY não configurada. Retornando reflexão simulada.")
            return "Simulação: Eu foquei demais na posse de bola do time da casa e ignorei que o time de fora tinha uma alta eficiência em contra-ataques, resultando em menos gols que o esperado."

        try:
            # Para texto simples e reflexivo, podemos usar o flash (ou pro) normal,
            # não precisamos do JSON mode para a lição, pois é texto livre.
            model_reflexao = genai.GenerativeModel("gemini-1.5-flash")

            prompt = (
                f"Sua análise falhou.\n\n"
                f"Contexto dos dados brutos pré-jogo:\n{json.dumps(dados_brutos, indent=2)}\n\n"
                f"O que você previu:\n{json.dumps(palpite_ia, indent=2)}\n\n"
                f"O que realmente aconteceu no jogo:\n{json.dumps(resultado_real, indent=2)}\n\n"
                f"Comando: Analise os dados brutos novamente e identifique qual padrão estatístico ou informação você ignorou que levou a esse erro. Seja técnico e direto em 1 ou 2 parágrafos."
            )

            print("Enviando dados para o Gemini refletir sobre o erro...")
            response = model_reflexao.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"Erro ao chamar a API do Gemini para reflexão: {e}")
            return "Erro técnico ao gerar reflexão. Possível falha na API."
