<script lang="ts">
  import { Loader2, Brain, Zap, Circle } from "lucide-svelte";

  export let text: string = "처리 중...";
  export let size: "sm" | "md" | "lg" | "xl" = "md";
  export let variant: "default" | "brain" | "pulse" | "dots" = "default";
  export let color: string = "text-claude-orange";
  export let centered: boolean = true;

  // 크기별 스타일
  $: sizeClasses = {
    sm: { spinner: 16, text: "text-sm" },
    md: { spinner: 24, text: "text-base" },
    lg: { spinner: 32, text: "text-lg" },
    xl: { spinner: 48, text: "text-xl" },
  };

  $: currentSize = sizeClasses[size];
</script>

<div
  class="flex {centered
    ? 'items-center justify-center'
    : 'items-start'} space-x-3 py-4"
>
  <!-- 스피너 아이콘 -->
  <div class="flex-shrink-0">
    {#if variant === "brain"}
      <Brain size={currentSize.spinner} class="{color} animate-pulse" />
    {:else if variant === "pulse"}
      <Circle size={currentSize.spinner} class="{color} animate-ping" />
    {:else if variant === "dots"}
      <!-- 점 3개 애니메이션 -->
      <div class="flex space-x-1">
        <div
          class="w-2 h-2 bg-claude-orange rounded-full animate-bounce"
          style="animation-delay: 0ms"
        />
        <div
          class="w-2 h-2 bg-claude-orange rounded-full animate-bounce"
          style="animation-delay: 150ms"
        />
        <div
          class="w-2 h-2 bg-claude-orange rounded-full animate-bounce"
          style="animation-delay: 300ms"
        />
      </div>
    {:else}
      <Loader2 size={currentSize.spinner} class="{color} animate-spin" />
    {/if}
  </div>

  <!-- 텍스트 -->
  {#if text}
    <div class="flex-1">
      <p class="{currentSize.text} text-dark-300 font-medium">
        {text}
      </p>
    </div>
  {/if}
</div>

<!-- 사용 예시 (주석):
  <LoadingSpinner text="AI 응답 생성 중..." size="lg" variant="brain" />
  <LoadingSpinner text="데이터 로딩 중..." size="md" variant="default" />
  <LoadingSpinner text="처리 중..." size="sm" variant="dots" centered={false} />
  -->

<!-- 추가 스타일 옵션들 -->
<style>
  /* 커스텀 바운스 애니메이션 */
  @keyframes customBounce {
    0%,
    80%,
    100% {
      transform: scale(0);
    }
    40% {
      transform: scale(1);
    }
  }

  /* 펄스 효과 */
  @keyframes customPulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  /* 회전 애니메이션 개선 */
  @keyframes improvedSpin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>
