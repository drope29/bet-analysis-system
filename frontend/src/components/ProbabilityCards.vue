<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 w-full">
    <div
      v-for="(dados, mercado) in palpite"
      :key="mercado"
      class="rounded-xl p-5 border flex flex-col justify-between shadow-lg transform transition hover:scale-105"
      :class="getColorClass(dados.confianca)"
    >
      <div>
        <div class="flex justify-between items-start mb-2">
          <h3 class="text-sm font-bold uppercase tracking-wide opacity-80">{{ formatMercado(mercado) }}</h3>
          <span class="text-xl font-black">{{ dados.confianca }}</span>
        </div>
        <p class="text-2xl font-bold mb-3">{{ dados.palpite }}</p>
      </div>

      <div>
        <p class="text-xs opacity-90 leading-relaxed border-t border-black border-opacity-20 pt-2 mt-2 mb-2">
          {{ dados.justificativa }}
        </p>

        <div v-if="dados.alta_convergencia" class="inline-flex items-center px-2 py-1 rounded-md text-[10px] font-bold bg-black bg-opacity-20 text-white mt-1 border border-white border-opacity-30">
          <span class="mr-1">🔥</span> Alta Convergência Estatística
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  palpite: {
    type: Object,
    required: true
  }
})

const formatMercado = (str) => {
  const map = {
    'vencedor_1x2': '1X2 (Vencedor)',
    'over_under_gols': 'Over/Under Gols',
    'escanteios': 'Escanteios',
    'cartoes': 'Cartões',
    'chutes_ao_gol': 'Chutes ao Gol'
  }
  return map[str] || str.replace(/_/g, ' ')
}

const getColorClass = (confiancaStr) => {
  // Extrai o numero da string ex: "85%" -> 85
  const match = String(confiancaStr).match(/(\d+)/)
  if (!match) return 'bg-gray-700 border-gray-600 text-white'

  const val = parseInt(match[0], 10)

  if (val > 84) {
    return 'bg-emerald-600 border-emerald-500 text-white' // Verde Intenso
  } else if (val >= 70) {
    return 'bg-lime-500 border-lime-400 text-gray-900' // Verde Lima (Bom valor)
  } else {
    return 'bg-amber-400 border-amber-300 text-gray-900' // Amarelo (Risco Elevado)
  }
}
</script>
