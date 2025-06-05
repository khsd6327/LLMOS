<script lang="ts">
  import { onMount } from "svelte";

  let mounted = false;

  onMount(() => {
    mounted = true;
  });
</script>

{#if mounted}
  <div class="flex items-center space-x-2">
    <div class="flex space-x-1">
      <div
        class="w-2 h-2 bg-dark-400 rounded-full animate-bounce"
        style="animation-delay: 0ms;"
      />
      <div
        class="w-2 h-2 bg-dark-400 rounded-full animate-bounce"
        style="animation-delay: 150ms;"
      />
      <div
        class="w-2 h-2 bg-dark-400 rounded-full animate-bounce"
        style="animation-delay: 300ms;"
      />
    </div>
    <span class="text-sm text-dark-500">AI가 응답을 생각하고 있습니다...</span>
  </div>
{/if}

<style>
  @keyframes bounce {
    0%,
    20%,
    53%,
    80%,
    100% {
      transform: translateY(0px);
    }
    40%,
    43% {
      transform: translateY(-8px);
    }
    70% {
      transform: translateY(-4px);
    }
    90% {
      transform: translateY(-2px);
    }
  }

  .animate-bounce {
    animation: bounce 1.4s ease-in-out infinite;
  }
</style>
