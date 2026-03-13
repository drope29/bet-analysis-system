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

    def analisar(self, dados_casa, dados_fora, erros_passados=None):
        """
        Envia os dados para o Gemini e retorna a análise estruturada em JSON.
        """
        if not gemini_api_key:
            print("Aviso: GEMINI_API_KEY não configurada. Retornando palpite simulado.")
            return self._gerar_palpite_simulado(dados_casa, dados_fora)

        # Se falhou a inicialização do modelo (ex: versão incompatível do SDK ou key inválida pro modelo)
        if not self.model:
            self.model = genai.GenerativeModel("gemini-pro") # Fallback pro modelo antigo sem json mode nativo

        # Preparar o prompt com a memória de erros
        prompt_erros = ""
        if erros_passados and len(erros_passados) > 0:
            lista_erros = "\n".join([f"- {erro}" for erro in erros_passados])
            prompt_erros = f"\n\nEvite os seguintes erros cometidos em análises passadas:\n{lista_erros}"

        prompt = (
            f"Dados do Time da Casa ({dados_casa.get('time', 'Casa')}): {json.dumps(dados_casa.get('ultimos_10_jogos', []))}\n\n"
            f"Dados do Time de Fora ({dados_fora.get('time', 'Fora')}): {json.dumps(dados_fora.get('ultimos_10_jogos', []))}\n\n"
            f"Gere uma análise estruturada contendo as porcentagens de confiança e justificativas para os mercados: "
            f"Vencedor (1x2), Over/Under Gols, Escanteios, Cartões e Chutes ao Gol."
            f"{prompt_erros}"
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

    def _gerar_palpite_simulado(self, dados_casa, dados_fora):
        # Mock do retorno da IA para caso a API falhe ou a chave não exista
        time_casa = dados_casa.get("time", "Casa")
        time_fora = dados_fora.get("time", "Fora")

        return {
            "vencedor_1x2": {
                "palpite": time_casa,
                "confianca": "65%",
                "justificativa": f"Simulação: {time_casa} costuma ter melhor posse de bola."
            },
            "over_under_gols": {
                "palpite": "Over 2.5",
                "confianca": "70%",
                "justificativa": "A média de gols simulada de ambos é alta."
            },
            "escanteios": {
                "palpite": "Over 8.5",
                "confianca": "80%",
                "justificativa": "Muitos ataques pelas pontas nos últimos jogos."
            },
            "cartoes": {
                "palpite": "Under 4.5",
                "confianca": "60%",
                "justificativa": "Ambos os times simulam poucas faltas."
            },
            "chutes_ao_gol": {
                "palpite": "Casa Over 4.5",
                "confianca": "55%",
                "justificativa": "Agressividade nas finalizações dentro de casa."
            }
        }
