<!-- ted-os-project/frontend/src/lib/components/ui/SuccessToast.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { clearSuccess } from "$lib/stores";
  import { X, CheckCircle } from "lucide-svelte";

  export let message: string;

  let visible = false;

  onMount(() => {
    visible = true;

    // 3초 후 자동 제거
    const timer = setTimeout(() => {
      visible = false;
      setTimeout(clearSuccess, 300); // 애니메이션 완료 후 제거
    }, 3000);

    return () => clearTimeout(timer);
  });

  function handleClose() {
    visible = false;
    setTimeout(clearSuccess, 300);
  }
</script>

<div class="fixed top-4 right-4 z-50 max-w-sm">
  <div
    class="bg-green-900/90 border border-green-700 rounded-lg p-4 shadow-xl backdrop-blur-sm transition-all duration-300 {visible
      ? 'translate-x-0 opacity-100'
      : 'translate-x-full opacity-0'}"
  >
    <div class="flex items-start space-x-3">
      <CheckCircle size={20} class="text-green-400 flex-shrink-0 mt-0.5" />

      <div class="flex-1">
        <div class="text-sm font-medium text-green-100 mb-1">성공</div>
        <div class="text-sm text-green-200">
          {message}
        </div>
      </div>

      <button
        class="text-green-400 hover:text-green-300 transition-colors"
        on:click={handleClose}
      >
        <X size={16} />
      </button>
    </div>
  </div>
</div>
