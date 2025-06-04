<script lang="ts">
  import {
    selectedProvider,
    selectedModel,
    temperature,
    maxTokens,
  } from "$lib/stores";
  import {
    MODELS_DATA,
    getAllProviders,
    getModelsForProvider,
    getModelConfig,
    formatCost,
  } from "$lib/models";
  import { ChevronDown, Info, Thermometer, Type } from "lucide-svelte";

  let showDetails = false;

  // 모든 제공업체 목록
  $: providers = getAllProviders();

  // 현재 제공업체의 모델 목록
  $: currentModels = getModelsForProvider($selectedProvider);
  $: modelEntries = Object.entries(currentModels);

  // 현재 선택된 모델의 상세 정보
  $: currentModelConfig = getModelConfig($selectedProvider, $selectedModel);

  // 제공업체 변경 시 해당 제공업체의 첫 번째 모델로 자동 변경
  function handleProviderChange() {
    const models = getModelsForProvider($selectedProvider);
    const modelKeys = Object.keys(models);
    if (modelKeys.length > 0) {
      selectedModel.set(modelKeys[0]);
    }
  }

  // Temperature 슬라이더 레이블
  function getTemperatureLabel(temp: number): string {
    if (temp <= 0.2) return "매우 일관적";
    if (temp <= 0.5) return "일관적";
    if (temp <= 0.8) return "균형잡힌";
    if (temp <= 1.2) return "창의적";
    return "매우 창의적";
  }
</script>

<div class="space-y-4">
  <!-- 제공업체 선택 -->
  <div>
    <label class="block text-xs font-medium text-dark-400 mb-2">
      AI 제공업체
    </label>
    <div class="relative">
      <select
        bind:value={$selectedProvider}
        on:change={handleProviderChange}
        class="w-full appearance-none bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-sm text-dark-100 pr-8 focus:outline-none focus:ring-2 focus:ring-claude-orange/50 focus:border-claude-orange/50"
      >
        {#each providers as provider}
          <option value={provider}>{provider}</option>
        {/each}
      </select>
      <ChevronDown
        size={16}
        class="absolute right-2 top-3 text-dark-400 pointer-events-none"
      />
    </div>
  </div>

  <!-- 모델 선택 -->
  <div>
    <label class="block text-xs font-medium text-dark-400 mb-2"> 모델 </label>
    <div class="relative">
      <select
        bind:value={$selectedModel}
        class="w-full appearance-none bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-sm text-dark-100 pr-8 focus:outline-none focus:ring-2 focus:ring-claude-orange/50 focus:border-claude-orange/50"
      >
        {#each modelEntries as [key, model]}
          <option value={key}>{model.display_name}</option>
        {/each}
      </select>
      <ChevronDown
        size={16}
        class="absolute right-2 top-3 text-dark-400 pointer-events-none"
      />
    </div>
  </div>

  <!-- 모델 정보 -->
  {#if currentModelConfig}
    <div class="bg-dark-800/50 rounded-lg p-3 space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs font-medium text-dark-400">모델 정보</span>
        <button
          class="btn-icon p-1"
          on:click={() => (showDetails = !showDetails)}
        >
          <Info size={14} />
        </button>
      </div>

      <div class="text-xs text-dark-300">
        {currentModelConfig.description}
      </div>

      {#if showDetails}
        <div class="pt-2 border-t border-dark-700 space-y-1 text-xs">
          <div class="flex justify-between">
            <span class="text-dark-400">최대 토큰:</span>
            <span class="text-dark-200"
              >{currentModelConfig.max_tokens?.toLocaleString()}</span
            >
          </div>
          <div class="flex justify-between">
            <span class="text-dark-400">입력 비용:</span>
            <span class="text-dark-200"
              >{formatCost(currentModelConfig.input_cost_per_1k)}/1K</span
            >
          </div>
          <div class="flex justify-between">
            <span class="text-dark-400">출력 비용:</span>
            <span class="text-dark-200"
              >{formatCost(currentModelConfig.output_cost_per_1k)}/1K</span
            >
          </div>
          <div class="flex justify-between">
            <span class="text-dark-400">스트리밍:</span>
            <span class="text-dark-200"
              >{currentModelConfig.supports_streaming ? "✅" : "❌"}</span
            >
          </div>
          <div class="flex justify-between">
            <span class="text-dark-400">함수 호출:</span>
            <span class="text-dark-200"
              >{currentModelConfig.supports_functions ? "✅" : "❌"}</span
            >
          </div>
          <div class="flex justify-between">
            <span class="text-dark-400">비전:</span>
            <span class="text-dark-200"
              >{currentModelConfig.supports_vision ? "✅" : "❌"}</span
            >
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Temperature 설정 -->
  <div>
    <div class="flex items-center justify-between mb-2">
      <label class="flex items-center text-xs font-medium text-dark-400">
        <Thermometer size={14} class="mr-1" />
        Temperature
      </label>
      <span class="text-xs text-dark-300"
        >{$temperature} - {getTemperatureLabel($temperature)}</span
      >
    </div>
    <input
      type="range"
      min="0"
      max="2"
      step="0.1"
      bind:value={$temperature}
      class="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer slider"
    />
    <div class="flex justify-between text-xs text-dark-500 mt-1">
      <span>일관적</span>
      <span>창의적</span>
    </div>
  </div>

  <!-- Max Tokens 설정 -->
  <div>
    <div class="flex items-center justify-between mb-2">
      <label class="flex items-center text-xs font-medium text-dark-400">
        <Type size={14} class="mr-1" />
        최대 토큰
      </label>
      <span class="text-xs text-dark-300">{$maxTokens.toLocaleString()}</span>
    </div>
    <input
      type="range"
      min="100"
      max={currentModelConfig?.max_tokens || 32768}
      step="100"
      bind:value={$maxTokens}
      class="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer slider"
    />
    <div class="flex justify-between text-xs text-dark-500 mt-1">
      <span>100</span>
      <span>{currentModelConfig?.max_tokens?.toLocaleString() || "32K"}</span>
    </div>
  </div>
</div>

<style>
  /* 커스텀 슬라이더 스타일 */
  .slider::-webkit-slider-thumb {
    appearance: none;
    height: 16px;
    width: 16px;
    border-radius: 50%;
    background: #ff6b35;
    cursor: pointer;
    border: 2px solid #1e293b;
  }

  .slider::-moz-range-thumb {
    height: 16px;
    width: 16px;
    border-radius: 50%;
    background: #ff6b35;
    cursor: pointer;
    border: 2px solid #1e293b;
  }

  .slider::-webkit-slider-track {
    height: 8px;
    border-radius: 4px;
    background: #475569;
  }

  .slider::-moz-range-track {
    height: 8px;
    border-radius: 4px;
    background: #475569;
  }
</style>
