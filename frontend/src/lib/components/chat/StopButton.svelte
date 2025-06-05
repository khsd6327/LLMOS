<!-- ted-os-project/frontend/src/lib/components/chat/StopButton.svelte -->
<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { StopCircle, Brain, Loader2 } from "lucide-svelte";

  export let isGenerating: boolean = false;
  export let fullWidth: boolean = true;
  export let variant: "primary" | "secondary" | "danger" = "danger";

  const dispatch = createEventDispatcher();

  function handleStop() {
    dispatch("stop");
  }

  // 버튼 스타일 결정
  $: buttonClass =
    variant === "danger"
      ? "btn bg-red-600 hover:bg-red-700 text-white border-red-600"
      : variant === "primary"
      ? "btn-primary"
      : "btn-secondary";
</script>

{#if isGenerating}
  <!-- AI 응답 생성 중 상태 표시 -->
  <div class="space-y-4">
    <!-- 상태 메시지 -->
    <div class="flex items-center justify-center space-x-3 py-4">
      <div class="flex items-center space-x-2">
        <Loader2 size={20} class="animate-spin text-claude-orange" />
        <Brain size={20} class="text-claude-orange animate-pulse" />
      </div>
      <div class="text-center">
        <h3 class="text-lg font-semibold text-dark-100">
          🤖 AI 응답 생성 중...
        </h3>
        <p class="text-sm text-dark-400">잠시만 기다려주세요</p>
      </div>
    </div>

    <!-- 중단 버튼 -->
    <button
      class="{buttonClass} {fullWidth
        ? 'w-full'
        : ''} transition-all duration-200 hover:scale-[1.02]"
      on:click={handleStop}
      type="button"
    >
      <StopCircle size={18} class="mr-2" />
      🛑 응답 중단
    </button>

    <!-- 안내 메시지 -->
    <div class="text-center space-y-1">
      <p class="text-xs text-dark-500">
        💡 원하지 않는 응답이 생성되고 있다면 위 버튼을 눌러 중단할 수 있습니다.
      </p>
      <p class="text-xs text-dark-500">🔄 Enter: 전송 | Shift+Enter: 줄바꿈</p>
    </div>
  </div>
{:else}
  <!-- 대기 상태 (숨김) -->
  <div class="hidden" />
{/if}

<style>
  /* 부드러운 애니메이션 */
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-950;
  }

  /* 호버 효과 강화 */
  .btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  }
</style>
