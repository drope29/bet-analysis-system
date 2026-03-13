<template>
  <div class="flex-grow flex flex-col bg-gray-900 h-screen relative">

    <!-- Mensagens do Chat -->
    <div class="flex-grow overflow-y-auto p-6 space-y-6 pb-32" ref="messagesContainer">
      <div v-for="(msg, idx) in messages" :key="idx" class="max-w-4xl mx-auto w-full">

        <!-- Mensagem do Usuário -->
        <div v-if="msg.sender === 'user'" class="flex justify-end">
          <div class="bg-blue-600 text-white p-4 rounded-2xl rounded-tr-sm shadow-md max-w-[70%] text-sm">
            <p class="font-semibold mb-1 opacity-70 text-xs flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
              </svg>
              Operador
            </p>
            {{ msg.text }}
          </div>
        </div>

        <!-- Mensagem do Sistema / Loading -->
        <div v-if="msg.sender === 'system'" class="flex justify-start">
          <div class="flex flex-col items-start max-w-full w-full">
            <div class="flex items-center text-gray-400 mb-2 ml-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
              </svg>
              <span class="font-semibold text-xs tracking-wider uppercase text-green-400">Terminal Analítico</span>
            </div>

            <div class="w-full">
              <!-- Log de Pensamento (Reativo) -->
              <ThoughtLog v-if="msg.isProcessing" :status="processingStatus" />

              <!-- Cards de Probabilidade (Resultados) -->
              <ProbabilityCards v-if="msg.palpite_ia" :palpite="msg.palpite_ia" />

              <!-- Mensagem de texto caso haja erro ou recado -->
              <div v-if="msg.text && !msg.palpite_ia && !msg.isProcessing" class="bg-gray-800 border border-gray-700 p-4 rounded-xl rounded-tl-sm text-sm text-gray-300 w-auto inline-block shadow-md">
                {{ msg.text }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Box -->
    <div class="absolute bottom-0 w-full bg-gray-900 border-t border-gray-700 p-4 pt-6">
      <div class="max-w-4xl mx-auto flex">
        <div class="relative flex-grow flex space-x-2">
          <input
            type="text"
            v-model="timeCasa"
            placeholder="Time da Casa"
            class="w-2/5 bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 placeholder-gray-500"
            @keyup.enter="analisar"
            :disabled="isProcessing"
          >
          <div class="flex items-center text-gray-500 font-bold px-1">X</div>
          <input
            type="text"
            v-model="timeFora"
            placeholder="Time de Fora"
            class="w-2/5 bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 placeholder-gray-500"
            @keyup.enter="analisar"
            :disabled="isProcessing"
          >
          <input
            type="number"
            step="0.01"
            v-model="oddInformada"
            placeholder="Odd (ex: 1.80)"
            class="w-1/5 bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 placeholder-gray-500"
            @keyup.enter="analisar"
            :disabled="isProcessing"
          >
          <button
            @click="analisar"
            :disabled="isProcessing || !timeCasa || !timeFora || !oddInformada"
            class="bg-green-600 hover:bg-green-500 text-white px-6 py-3 rounded-lg font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center shadow-lg whitespace-nowrap"
          >
            <span v-if="!isProcessing">Analisar</span>
            <svg v-else class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </button>
        </div>
      </div>
      <p class="text-center text-xs text-gray-600 mt-2">
        Pressione Enter ou clique em Analisar para iniciar a coleta de dados brutos e inferência.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import ThoughtLog from './ThoughtLog.vue'
import ProbabilityCards from './ProbabilityCards.vue'

const timeCasa = ref('')
const timeFora = ref('')
const oddInformada = ref('')
const isProcessing = ref(false)
const processingStatus = ref(0)
const messagesContainer = ref(null)

const messages = ref([
  {
    sender: 'system',
    text: 'Sistemas online. Terminal de análise preditiva pronto. Insira os confrontos abaixo para iniciar a raspagem de dados e a inferência probabilística.',
    isProcessing: false
  }
])

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const simularPensamento = () => {
  processingStatus.value = 0

  // Simula as etapas do raciocínio enquanto a API processa em background
  const steps = [
    { time: 500, status: 1 },  // Coletando estatísticas...
    { time: 2500, status: 2 }, // Consultando banco de lições...
    { time: 4000, status: 3 }, // Aplicando modelos matemáticos...
    { time: 6000, status: 4 }, // Gerando análise final...
  ]

  steps.forEach(step => {
    setTimeout(() => {
      if (isProcessing.value) { // Só avança se ainda estiver processando
        processingStatus.value = step.status
      }
    }, step.time)
  })
}

const analisar = async () => {
  if (!timeCasa.value || !timeFora.value || isProcessing.value) return

  const matchStr = `${timeCasa.value} x ${timeFora.value} (Odd: ${oddInformada.value})`

  // Adiciona a mensagem do usuario
  messages.value.push({ sender: 'user', text: `Analisar confronto: ${matchStr}` })

  // Prepara o sistema
  isProcessing.value = true
  const systemMsgIndex = messages.value.push({
    sender: 'system',
    isProcessing: true,
    palpite_ia: null
  }) - 1

  scrollToBottom()
  simularPensamento()

  try {
    const response = await fetch('http://127.0.0.1:5000/analisar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        time_casa: timeCasa.value,
        time_fora: timeFora.value,
        odd: parseFloat(oddInformada.value)
      })
    })

    const data = await response.json()

    // Atualiza a mensagem do sistema com a resposta final
    if (response.ok) {
        messages.value[systemMsgIndex].isProcessing = false
        messages.value[systemMsgIndex].palpite_ia = data.palpite_ia
    } else {
        messages.value[systemMsgIndex].isProcessing = false
        messages.value[systemMsgIndex].text = `Erro na análise: ${data.erro || 'Desconhecido'}`
    }

  } catch (error) {
    console.error('Erro de conexão:', error)
    messages.value[systemMsgIndex].isProcessing = false
    messages.value[systemMsgIndex].text = 'Erro de conexão com o terminal backend. Verifique se o servidor Flask está rodando.'
  } finally {
    isProcessing.value = false
    timeCasa.value = ''
    timeFora.value = ''
    oddInformada.value = ''
    scrollToBottom()
  }
}
</script>
