<template>
  <div class="bg-gray-800 border-l-4 border-green-500 rounded-r-lg p-4 mb-4 shadow-lg w-full max-w-lg font-mono text-sm">
    <div class="flex items-center mb-3 border-b border-gray-700 pb-2">
      <div class="w-3 h-3 rounded-full bg-red-500 mr-1.5"></div>
      <div class="w-3 h-3 rounded-full bg-yellow-500 mr-1.5"></div>
      <div class="w-3 h-3 rounded-full bg-green-500 mr-3"></div>
      <span class="text-gray-400">Raciocínio da IA</span>
    </div>

    <ul class="space-y-3">
      <li class="flex items-center opacity-0 transition-opacity duration-500" :class="{ 'opacity-100': status >= 1 }">
        <svg v-if="status > 1" class="w-4 h-4 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <svg v-else class="animate-spin w-4 h-4 mr-2 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span :class="{ 'text-green-400': status > 1, 'text-gray-300': status === 1 }">Coletando estatísticas dos últimos 10 jogos...</span>
      </li>

      <li class="flex items-center opacity-0 transition-opacity duration-500 delay-150" :class="{ 'opacity-100': status >= 2 }">
        <svg v-if="status > 2" class="w-4 h-4 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <svg v-else class="animate-spin w-4 h-4 mr-2 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span :class="{ 'text-green-400': status > 2, 'text-gray-300': status === 2 }">Consultando banco de lições aprendidas (Reds passados)...</span>
      </li>

      <li class="flex items-center opacity-0 transition-opacity duration-500 delay-300" :class="{ 'opacity-100': status >= 3 }">
        <svg v-if="status > 3" class="w-4 h-4 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <svg v-else class="animate-spin w-4 h-4 mr-2 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span :class="{ 'text-green-400': status > 3, 'text-gray-300': status === 3 }">Aplicando modelos matemáticos (Poisson e Média Ponderada)...</span>
      </li>

      <li class="flex items-center opacity-0 transition-opacity duration-500 delay-500" :class="{ 'opacity-100': status >= 4 }">
        <svg v-if="status > 4" class="w-4 h-4 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <svg v-else class="animate-spin w-4 h-4 mr-2 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span :class="{ 'text-blue-400 font-bold': status === 4, 'text-green-400': status > 4 }">Gerando análise final de confiança...</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  status: {
    type: Number,
    required: true
  }
})
</script>
