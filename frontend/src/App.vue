<script setup>
import Sidebar from './components/Sidebar.vue'
import ChatInterface from './components/ChatInterface.vue'
</script>

<template>
  <div class="flex h-screen bg-gray-900 overflow-hidden font-sans text-gray-100 selection:bg-green-500 selection:text-gray-900">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Chat Area -->
    <main class="flex-1 relative">
      <ChatInterface />
    </main>
  </div>
</template>

<style>
/* Oculta scrollbar mas mantém a funcionalidade */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #374151; /* gray-700 */
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #4b5563; /* gray-600 */
}
</style>
