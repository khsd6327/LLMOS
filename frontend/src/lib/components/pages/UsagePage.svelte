<!-- ted-os-project/frontend/src/lib/components/pages/UsagePage.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { usageStats } from "$lib/stores";
  import { api } from "$lib/api";
  import { formatCost, formatTokens } from "$lib/models";
  import { showError } from "$lib/stores";
  import {
    BarChart3,
    TrendingUp,
    DollarSign,
    Zap,
    MessageCircle,
    RefreshCw,
    Calendar,
    Clock,
  } from "lucide-svelte";

  let loading = false;

  // 사용량 통계 새로고침
  async function refreshStats() {
    loading = true;
    try {
      const stats = await api.getUsageStats();
      usageStats.set(stats);
    } catch (error) {
      console.error("사용량 통계 로드 실패:", error);
      showError("사용량 통계를 불러올 수 없습니다.");
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    if (!$usageStats) {
      refreshStats();
    }
  });

  // 차트 데이터 준비
  $: chartData = $usageStats?.usage_trends || [];
  $: modelUsage = $usageStats?.usage_by_model || {};

  // 상위 사용 모델 (최대 5개)
  $: topModels = Object.entries(modelUsage)
    .sort(([, a], [, b]) => b.tokens - a.tokens)
    .slice(0, 5);
</script>

<div class="flex-1 overflow-y-auto p-6 space-y-6">
  <!-- 페이지 헤더 -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-dark-100">사용량 통계</h1>
      <p class="text-dark-400 mt-1">API 사용량과 비용을 추적하고 분석하세요.</p>
    </div>

    <button
      class="btn-secondary {loading ? 'animate-spin' : ''}"
      on:click={refreshStats}
      disabled={loading}
    >
      <RefreshCw size={16} class="mr-2" />
      새로고침
    </button>
  </div>

  {#if $usageStats}
    <!-- 주요 메트릭 카드 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- 오늘 요청 수 -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div
            class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center"
          >
            <MessageCircle size={20} class="text-blue-400" />
          </div>
          <span class="text-xs text-dark-500">오늘</span>
        </div>
        <div class="text-2xl font-bold text-dark-100 mb-1">
          {$usageStats.today_usage.total_requests}
        </div>
        <div class="text-sm text-dark-400">요청 수</div>
      </div>

      <!-- 오늘 토큰 사용량 -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div
            class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center"
          >
            <Zap size={20} class="text-green-400" />
          </div>
          <span class="text-xs text-dark-500">오늘</span>
        </div>
        <div class="text-2xl font-bold text-dark-100 mb-1">
          {formatTokens($usageStats.today_usage.total_tokens)}
        </div>
        <div class="text-sm text-dark-400">토큰</div>
      </div>

      <!-- 오늘 비용 -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div
            class="w-10 h-10 bg-claude-orange/20 rounded-lg flex items-center justify-center"
          >
            <DollarSign size={20} class="text-claude-orange" />
          </div>
          <span class="text-xs text-dark-500">오늘</span>
        </div>
        <div class="text-2xl font-bold text-dark-100 mb-1">
          {formatCost($usageStats.today_usage.total_cost)}
        </div>
        <div class="text-sm text-dark-400">비용</div>
      </div>

      <!-- 예상 월간 비용 -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div
            class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center"
          >
            <TrendingUp size={20} class="text-purple-400" />
          </div>
          <span class="text-xs text-dark-500">예상</span>
        </div>
        <div class="text-2xl font-bold text-dark-100 mb-1">
          {formatCost($usageStats.estimated_monthly_cost)}
        </div>
        <div class="text-sm text-dark-400">월간 비용</div>
      </div>
    </div>

    <!-- 기간별 사용량 비교 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 주간 vs 월간 비교 -->
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-dark-100 mb-4 flex items-center">
          <Calendar size={20} class="mr-2" />
          기간별 사용량
        </h2>

        <div class="space-y-4">
          <!-- 주간 사용량 -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-dark-400">지난 7일</span>
              <span class="text-sm font-medium text-dark-200">
                {formatCost($usageStats.weekly_usage.total_cost)}
              </span>
            </div>
            <div class="grid grid-cols-3 gap-4 text-xs">
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {$usageStats.weekly_usage.total_requests}
                </div>
                <div class="text-dark-500">요청</div>
              </div>
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {formatTokens($usageStats.weekly_usage.total_tokens)}
                </div>
                <div class="text-dark-500">토큰</div>
              </div>
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {formatCost($usageStats.weekly_usage.total_cost)}
                </div>
                <div class="text-dark-500">비용</div>
              </div>
            </div>
          </div>

          <!-- 월간 사용량 -->
          <div class="pt-4 border-t border-dark-700">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-dark-400">이번 달</span>
              <span class="text-sm font-medium text-dark-200">
                {formatCost($usageStats.monthly_usage.total_cost)}
              </span>
            </div>
            <div class="grid grid-cols-3 gap-4 text-xs">
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {$usageStats.monthly_usage.total_requests}
                </div>
                <div class="text-dark-500">요청</div>
              </div>
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {formatTokens($usageStats.monthly_usage.total_tokens)}
                </div>
                <div class="text-dark-500">토큰</div>
              </div>
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {formatCost($usageStats.monthly_usage.total_cost)}
                </div>
                <div class="text-dark-500">비용</div>
              </div>
            </div>
          </div>

          <!-- 전체 사용량 -->
          <div class="pt-4 border-t border-dark-700">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-dark-400">전체 기간</span>
              <span class="text-sm font-medium text-dark-200">
                {formatCost($usageStats.total_usage.total_cost)}
              </span>
            </div>
            <div class="grid grid-cols-3 gap-4 text-xs">
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {$usageStats.total_usage.total_requests}
                </div>
                <div class="text-dark-500">요청</div>
              </div>
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {formatTokens($usageStats.total_usage.total_tokens)}
                </div>
                <div class="text-dark-500">토큰</div>
              </div>
              <div class="text-center">
                <div class="text-dark-300 font-medium">
                  {formatCost($usageStats.total_usage.total_cost)}
                </div>
                <div class="text-dark-500">비용</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 모델별 사용량 -->
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-dark-100 mb-4 flex items-center">
          <BarChart3 size={20} class="mr-2" />
          모델별 사용량 (상위 5개)
        </h2>

        {#if topModels.length > 0}
          <div class="space-y-3">
            {#each topModels as [modelName, stats]}
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-medium text-dark-200 truncate">
                    {modelName}
                  </span>
                  <span class="text-xs text-dark-400">
                    {formatCost(stats.cost)}
                  </span>
                </div>

                <!-- 사용량 바 -->
                <div class="w-full bg-dark-700 rounded-full h-2">
                  <div
                    class="bg-gradient-to-r from-claude-orange to-claude-blue h-2 rounded-full transition-all duration-500"
                    style="width: {Math.min(
                      100,
                      (stats.tokens /
                        Math.max(...topModels.map(([, s]) => s.tokens))) *
                        100
                    )}%"
                  />
                </div>

                <div
                  class="flex items-center justify-between text-xs text-dark-500"
                >
                  <span>{formatTokens(stats.tokens)} 토큰</span>
                  <span>{stats.requests} 요청</span>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="text-center py-8">
            <BarChart3 size={40} class="mx-auto text-dark-600 mb-4" />
            <p class="text-dark-400">모델 사용량 데이터가 없습니다.</p>
          </div>
        {/if}
      </div>
    </div>

    <!-- 일별 사용량 트렌드 -->
    {#if chartData.length > 0}
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-dark-100 mb-4 flex items-center">
          <TrendingUp size={20} class="mr-2" />
          일별 사용량 트렌드 (최근 7일)
        </h2>

        <div class="space-y-4">
          {#each chartData as day}
            <div class="flex items-center space-x-4">
              <div class="w-20 text-xs text-dark-400 font-mono">
                {new Date(day.date).toLocaleDateString("ko-KR", {
                  month: "short",
                  day: "numeric",
                })}
              </div>

              <div class="flex-1">
                <!-- 토큰 사용량 바 -->
                <div class="w-full bg-dark-700 rounded-full h-2 mb-1">
                  <div
                    class="bg-blue-500 h-2 rounded-full transition-all duration-500"
                    style="width: {Math.min(
                      100,
                      (day.tokens /
                        Math.max(...chartData.map((d) => d.tokens))) *
                        100
                    )}%"
                  />
                </div>

                <!-- 비용 바 -->
                <div class="w-full bg-dark-700 rounded-full h-2">
                  <div
                    class="bg-claude-orange h-2 rounded-full transition-all duration-500"
                    style="width: {Math.min(
                      100,
                      (day.cost / Math.max(...chartData.map((d) => d.cost))) *
                        100
                    )}%"
                  />
                </div>
              </div>

              <div class="w-24 text-right space-y-1">
                <div class="text-xs text-dark-300">
                  {formatTokens(day.tokens)}
                </div>
                <div class="text-xs text-dark-400">
                  {formatCost(day.cost)}
                </div>
              </div>
            </div>
          {/each}

          <!-- 범례 -->
          <div
            class="flex items-center justify-center space-x-6 pt-4 border-t border-dark-700"
          >
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 bg-blue-500 rounded-full" />
              <span class="text-xs text-dark-400">토큰 사용량</span>
            </div>
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 bg-claude-orange rounded-full" />
              <span class="text-xs text-dark-400">비용</span>
            </div>
          </div>
        </div>
      </div>
    {/if}
  {:else if loading}
    <!-- 로딩 상태 -->
    <div class="flex items-center justify-center h-64">
      <div class="animate-spin">
        <RefreshCw size={32} class="text-dark-400" />
      </div>
    </div>
  {:else}
    <!-- 데이터 없음 -->
    <div class="text-center py-12">
      <BarChart3 size={64} class="mx-auto text-dark-600 mb-4" />
      <h3 class="text-lg font-medium text-dark-300 mb-2">
        사용량 데이터가 없습니다
      </h3>
      <p class="text-dark-500 mb-4">
        AI와 대화를 시작하면 사용량이 기록됩니다.
      </p>
      <button class="btn-primary" on:click={refreshStats}> 새로고침 </button>
    </div>
  {/if}
</div>
