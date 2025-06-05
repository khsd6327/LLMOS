<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "$lib/api";
  import { showError } from "$lib/stores";
  import LoadingSpinner from "./LoadingSpinner.svelte";
  import {
    BarChart3,
    TrendingUp,
    Calendar,
    DollarSign,
    RefreshCw,
  } from "lucide-svelte";

  export let days: number = 7;
  export let showControls: boolean = true;

  let loading = false;
  let trendsData: any[] = [];
  let selectedPeriod = days;

  // 사용량 트렌드 데이터 로드
  async function loadUsageTrends() {
    loading = true;
    try {
      // 실제 구현에서는 백엔드 API 호출
      // const data = await api.getUsageTrends(selectedPeriod);

      // 임시 데이터 생성 (실제로는 백엔드에서 받아야 함)
      const today = new Date();
      trendsData = Array.from({ length: selectedPeriod }, (_, i) => {
        const date = new Date(today);
        date.setDate(date.getDate() - (selectedPeriod - 1 - i));

        return {
          date: date.toISOString().split("T")[0],
          tokens: Math.floor(Math.random() * 5000) + 1000,
          requests: Math.floor(Math.random() * 50) + 10,
          cost: (Math.random() * 0.5 + 0.1).toFixed(4),
        };
      });
    } catch (error) {
      console.error("사용량 트렌드 로드 실패:", error);
      showError("사용량 트렌드를 불러올 수 없습니다.");
    } finally {
      loading = false;
    }
  }

  // 날짜 포맷팅
  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
    });
  }

  // 최대값 계산 (차트 스케일용)
  $: maxTokens = Math.max(...trendsData.map((d) => d.tokens));
  $: maxRequests = Math.max(...trendsData.map((d) => d.requests));
  $: maxCost = Math.max(...trendsData.map((d) => parseFloat(d.cost)));

  // 기간 변경 처리
  function handlePeriodChange() {
    days = selectedPeriod;
    loadUsageTrends();
  }

  onMount(() => {
    loadUsageTrends();
  });
</script>

<div class="space-y-6">
  <!-- 헤더 및 컨트롤 -->
  <div class="flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <TrendingUp size={24} class="text-claude-orange" />
      <div>
        <h2 class="text-xl font-bold text-dark-100">📊 사용량 트렌드</h2>
        <p class="text-dark-400 text-sm">
          최근 {selectedPeriod}일간의 사용 패턴을 확인하세요
        </p>
      </div>
    </div>

    {#if showControls}
      <div class="flex items-center space-x-3">
        <!-- 기간 선택 -->
        <select
          bind:value={selectedPeriod}
          on:change={handlePeriodChange}
          class="bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-sm text-dark-100 focus:outline-none focus:ring-2 focus:ring-claude-orange/50"
        >
          <option value={7}>지난 7일</option>
          <option value={14}>지난 14일</option>
          <option value={30}>지난 30일</option>
        </select>

        <!-- 새로고침 버튼 -->
        <button
          class="btn-secondary {loading ? 'animate-spin' : ''}"
          on:click={loadUsageTrends}
          disabled={loading}
        >
          <RefreshCw size={16} class="mr-2" />
          새로고침
        </button>
      </div>
    {/if}
  </div>

  {#if loading}
    <LoadingSpinner text="트렌드 데이터를 불러오는 중..." size="lg" />
  {:else if trendsData.length === 0}
    <div class="text-center py-12">
      <TrendingUp size={48} class="mx-auto text-dark-600 mb-4" />
      <p class="text-dark-400">표시할 트렌드 데이터가 없습니다.</p>
    </div>
  {:else}
    <!-- 차트 영역 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 토큰 사용량 차트 -->
      <div class="card p-6">
        <div class="flex items-center space-x-2 mb-4">
          <BarChart3 size={20} class="text-blue-400" />
          <h3 class="text-lg font-semibold text-dark-100">일별 토큰 사용량</h3>
        </div>

        <div class="space-y-3">
          {#each trendsData as day, i}
            <div class="flex items-center space-x-3">
              <div class="w-16 text-xs text-dark-400 text-right">
                {formatDate(day.date)}
              </div>
              <div class="flex-1 relative">
                <div class="bg-dark-700 rounded-full h-6 overflow-hidden">
                  <div
                    class="bg-blue-500 h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                    style="width: {(day.tokens / maxTokens) * 100}%"
                  >
                    <span class="text-xs text-white font-medium">
                      {day.tokens.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>

      <!-- 비용 차트 -->
      <div class="card p-6">
        <div class="flex items-center space-x-2 mb-4">
          <DollarSign size={20} class="text-green-400" />
          <h3 class="text-lg font-semibold text-dark-100">일별 비용</h3>
        </div>

        <div class="space-y-3">
          {#each trendsData as day, i}
            <div class="flex items-center space-x-3">
              <div class="w-16 text-xs text-dark-400 text-right">
                {formatDate(day.date)}
              </div>
              <div class="flex-1 relative">
                <div class="bg-dark-700 rounded-full h-6 overflow-hidden">
                  <div
                    class="bg-green-500 h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                    style="width: {(parseFloat(day.cost) / maxCost) * 100}%"
                  >
                    <span class="text-xs text-white font-medium">
                      ${day.cost}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>

    <!-- 요약 통계 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div
        class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 text-center"
      >
        <div class="text-2xl font-bold text-blue-400">
          {trendsData
            .reduce((sum, day) => sum + day.tokens, 0)
            .toLocaleString()}
        </div>
        <div class="text-sm text-dark-400">총 토큰</div>
      </div>

      <div
        class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 text-center"
      >
        <div class="text-2xl font-bold text-purple-400">
          {trendsData
            .reduce((sum, day) => sum + day.requests, 0)
            .toLocaleString()}
        </div>
        <div class="text-sm text-dark-400">총 요청</div>
      </div>

      <div
        class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 text-center"
      >
        <div class="text-2xl font-bold text-green-400">
          ${trendsData
            .reduce((sum, day) => sum + parseFloat(day.cost), 0)
            .toFixed(4)}
        </div>
        <div class="text-sm text-dark-400">총 비용</div>
      </div>

      <div
        class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 text-center"
      >
        <div class="text-2xl font-bold text-claude-orange">
          {Math.round(
            trendsData.reduce((sum, day) => sum + day.tokens, 0) /
              trendsData.length
          ).toLocaleString()}
        </div>
        <div class="text-sm text-dark-400">일평균 토큰</div>
      </div>
    </div>

    <!-- 추세 분석 -->
    <div class="bg-dark-800/30 rounded-lg p-4">
      <h3 class="text-lg font-semibold text-dark-100 mb-3">📈 추세 분석</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div>
          <span class="text-dark-400">최고 사용일:</span>
          <div class="font-medium text-dark-200">
            {formatDate(
              trendsData.reduce((max, day) =>
                day.tokens > max.tokens ? day : max
              ).date
            )}
          </div>
        </div>
        <div>
          <span class="text-dark-400">최고 비용일:</span>
          <div class="font-medium text-dark-200">
            {formatDate(
              trendsData.reduce((max, day) =>
                parseFloat(day.cost) > parseFloat(max.cost) ? day : max
              ).date
            )}
          </div>
        </div>
        <div>
          <span class="text-dark-400">예상 월간 비용:</span>
          <div class="font-medium text-claude-orange">
            ${(
              (trendsData.reduce((sum, day) => sum + parseFloat(day.cost), 0) /
                trendsData.length) *
              30
            ).toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>
