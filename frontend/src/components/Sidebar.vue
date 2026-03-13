<template>
  <div class="w-64 bg-gray-800 border-r border-gray-700 h-screen flex flex-col p-4">
    <h1 class="text-xl font-bold text-green-400 mb-8 flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
      Bet Terminal
    </h1>

    <div class="flex-grow">
      <h2 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Dashboard de Assertividade</h2>

      <!-- Stats Cards -->
      <div class="space-y-4">
        <div class="bg-gray-700 rounded-lg p-4 border border-gray-600">
          <p class="text-gray-400 text-sm mb-1">Win Rate</p>
          <div class="flex items-end">
            <span class="text-3xl font-bold text-white">{{ stats.win_rate || '0%' }}</span>
            <span class="text-xs text-gray-400 ml-2 mb-1">histórico geral</span>
          </div>
        </div>

        <div class="bg-gray-700 rounded-lg p-4 border border-gray-600">
          <p class="text-gray-400 text-sm mb-1">Lições na Memória</p>
          <div class="flex items-end">
            <span class="text-3xl font-bold text-blue-400">{{ stats.licoes_memoria || 0 }}</span>
            <span class="text-xs text-gray-400 ml-2 mb-1">padrões aprendidos</span>
          </div>
        </div>

        <div class="flex space-x-2 mt-4">
            <div class="flex-1 bg-gray-700 rounded-lg p-2 text-center border border-gray-600">
              <p class="text-xs text-gray-400">Greens</p>
              <p class="text-xl font-semibold text-green-500">{{ stats.total_greens || 0 }}</p>
            </div>
            <div class="flex-1 bg-gray-700 rounded-lg p-2 text-center border border-gray-600">
              <p class="text-xs text-gray-400">Reds</p>
              <p class="text-xl font-semibold text-red-500">{{ stats.total_reds || 0 }}</p>
            </div>
        </div>
      </div>
    </div>

    <div class="mt-auto pt-4 border-t border-gray-700 text-xs text-gray-500 flex items-center">
      <div class="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
      Sistema Online
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({
  win_rate: '0%',
  licoes_memoria: 0,
  total_greens: 0,
  total_reds: 0
})

const fetchStats = async () => {
  try {
    // Ajustar porta conforme o backend rodando
    const response = await fetch('http://127.0.0.1:5000/stats')
    if (response.ok) {
      stats.value = await response.json()
    }
  } catch (error) {
    console.error('Erro ao buscar estatísticas:', error)
  }
}

onMounted(() => {
  fetchStats()
  // Poderia ter um setInterval aqui para atualizar as estatisticas periodicamente
})
</script>
