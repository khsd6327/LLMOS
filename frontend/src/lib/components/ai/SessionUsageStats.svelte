<!-- ted-os-project/frontend/src/lib/components/ai/SessionUsageStats.svelte -->
<script lang="ts">
  import { usageStats, sessionDuration } from "$lib/stores";
  import { formatCost, formatTokens } from "$lib/models";
  import { Clock, Zap, DollarSign, MessageCircle } from "lucide-svelte";

  // 세션 시간을 포맷팅
  function formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  }

  // 세션 사용량 (임시 데이터 - 실제로는 백엔드에서 가져와야 함)
  let sessionStats = {
    requests: 0,
    tokens: 0,
    cost: 0,
  };

  // 사용량 통계에서 오늘의 데이터 추출
  $: todayStats = $usageStats?.today_usage || {
    total_requests: 0,
    total_tokens: 0,
    total_cost: 0,
  };

  $: monthlyStats = $usageStats?.monthly_usage || {
    total_requests: 0,
    total_tokens: 0,
    total_cost: 0,
  };
</script>

<div class="bg-dark-800/30 rounded-lg p-3 space-y-3">
  <h3 class="text-xs font-medium text-dark-400 uppercase tracking-wider">
    사용량 통계
  </h3>

  <!-- 세션 시간 -->
  <div class="flex items-center justify-between">
    <div class="flex items-center space-x-2">
      <Clock size={14} class="text-dark-500" />
      <span class="text-xs text-dark-400">세션 시간</span>
    </div>
    <span class="text-xs font-medium text-dark-200">
      {formatDuration($sessionDuration)}
    </span>
  </div>

  <!-- 오늘 사용량 -->
  <div class="space-y-2">
    <h4 class="text-xs font-medium text-dark-500">오늘</h4>

    <div class="grid grid-cols-3 gap-2 text-xs">
      <div class="text-center">
        <div class="text-dark-300 font-medium">
          {todayStats.total_requests}
        </div>
        <div class="text-dark-500">요청</div>
      </div>

      <div class="text-center">
        <div class="text-dark-300 font-medium">
          {formatTokens(todayStats.total_tokens)}
        </div>
        <div class="text-dark-500">토큰</div>
      </div>

      <div class="text-center">
        <div class="text-dark-300 font-medium">
          {formatCost(todayStats.total_cost)}
        </div>
        <div class="text-dark-500">비용</div>
      </div>
    </div>
  </div>

  <!-- 이번 달 사용량 -->
  <div class="space-y-2">
    <h4 class="text-xs font-medium text-dark-500">이번 달</h4>

    <div class="grid grid-cols-3 gap-2 text-xs">
      <div class="text-center">
        <div class="text-dark-300 font-medium">
          {monthlyStats.total_requests}
        </div>
        <div class="text-dark-500">요청</div>
      </div>

      <div class="text-center">
        <div class="text-dark-300 font-medium">
          {formatTokens(monthlyStats.total_tokens)}
        </div>
        <div class="text-dark-500">토큰</div>
      </div>

      <div class="text-center">
        <div class="text-dark-300 font-medium">
          {formatCost(monthlyStats.total_cost)}
        </div>
        <div class="text-dark-500">비용</div>
      </div>
    </div>
  </div>

  <!-- 예상 월간 비용 -->
  {#if $usageStats?.estimated_monthly_cost}
    <div class="pt-2 border-t border-dark-700">
      <div class="flex items-center justify-between">
        <span class="text-xs text-dark-400">예상 월간 비용</span>
        <span class="text-xs font-medium text-claude-orange">
          {formatCost($usageStats.estimated_monthly_cost)}
        </span>
      </div>
    </div>
  {/if}

  <!-- 상세 보기 링크 -->
  <button
    class="w-full text-xs text-claude-orange hover:text-claude-orange/80 transition-colors text-center pt-2 border-t border-dark-700"
    on:click={() => {
      // 상세 사용량 페이지로 이동하는 로직
      console.log("Navigate to usage details");
    }}
  >
    상세 보기 →
  </button>
</div>
