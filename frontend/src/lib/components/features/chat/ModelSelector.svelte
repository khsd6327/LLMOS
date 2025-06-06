<script lang="ts">
  import { selectedModel as globalSelectedModel } from "$lib/stores/chat";

  // 기본 모델 목록 (display용 provider와 API용 provider 분리)
  const basicModels = [
    {
      id: "chatgpt-4o-latest",
      provider: "ChatGPT", // 표시용
      apiProvider: "OpenAI", // API용
      model: "4o",
      display: "ChatGPT 4o",
    },
    {
      id: "claude-sonnet-4-20250514",
      provider: "Claude", // 표시용
      apiProvider: "Anthropic", // API용
      model: "4 Sonnet",
      display: "Claude 4 Sonnet",
    },
    {
      id: "gemini-2.5-flash-preview-05-20",
      provider: "Gemini", // 표시용
      apiProvider: "Google", // API용
      model: "2.5 Flash",
      display: "Gemini 2.5 Flash",
    },
  ];

  // 고급 모델 목록
  const advancedModels = [
    {
      id: "claude-opus-4-20250514",
      provider: "Claude",
      apiProvider: "Anthropic",
      model: "4 Opus",
      display: "Claude 4 Opus",
    },
    {
      id: "gemini-2.5-pro-preview-05-06",
      provider: "Gemini",
      apiProvider: "Google",
      model: "2.5 Pro",
      display: "Gemini 2.5 Pro",
    },
    {
      id: "gpt-4.1",
      provider: "ChatGPT",
      apiProvider: "OpenAI",
      model: "4.1",
      display: "ChatGPT 4.1",
    },
    {
      id: "o4-mini",
      provider: "ChatGPT",
      apiProvider: "OpenAI",
      model: "o4 mini",
      display: "ChatGPT o4 mini",
    },
  ];

  // 가벼운 모델 목록
  const lightModels = [
    {
      id: "gpt-4.1-mini",
      provider: "ChatGPT",
      apiProvider: "OpenAI",
      model: "4.1 mini",
      display: "ChatGPT 4.1 mini",
    },
    {
      id: "gpt-4.1-nano",
      provider: "ChatGPT",
      apiProvider: "OpenAI",
      model: "4.1 nano",
      display: "ChatGPT 4.1 nano",
    },
  ];

  let selectedModel = basicModels[1]; // Claude 4 Sonnet을 기본으로
  let isDropdownOpen = false;
  let showMoreModels = false;

  function selectModel(model: any) {
    selectedModel = model;
    // 전역 스토어에는 API용 provider로 업데이트
    globalSelectedModel.set({
      id: model.id,
      provider: model.apiProvider, // API용 provider 사용
      model: model.model,
      display: model.display,
    });
    isDropdownOpen = false;
    showMoreModels = false;
  }

  function toggleDropdown() {
    isDropdownOpen = !isDropdownOpen;
  }

  function toggleMoreModels() {
    showMoreModels = !showMoreModels;
  }
</script>

<div class="relative">
  <!-- 선택된 모델 표시 -->
  <button
    on:click={toggleDropdown}
    class="flex items-center space-x-2 px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
  >
    <span class="text-sm">
      <span class="text-gray-900 font-medium">{selectedModel.provider}</span>
      <span class="text-gray-500">{selectedModel.model}</span>
    </span>
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      class="text-gray-400 transform transition-transform {isDropdownOpen
        ? 'rotate-180'
        : ''}"
    >
      <polyline points="6,9 12,15 18,9" />
    </svg>
  </button>

  <!-- 드롭다운 메뉴 -->
  {#if isDropdownOpen}
    <div
      class="absolute top-full left-0 mt-1 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
    >
      <!-- 기본 모델들 -->
      <div class="p-2">
        {#each basicModels as model}
          <button
            on:click={() => selectModel(model)}
            class="w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors
                   {selectedModel.id === model.id ? 'bg-gray-50' : ''}"
          >
            <span class="text-sm">
              <span class="text-gray-900 font-medium">{model.provider}</span>
              <span class="text-gray-500">{model.model}</span>
            </span>
          </button>
        {/each}
      </div>

      <!-- 모델 더 보기 -->
      <div class="border-t border-gray-100">
        <button
          on:click={toggleMoreModels}
          class="w-full text-left px-5 py-3 text-sm text-gray-600 hover:bg-gray-50 transition-colors flex items-center justify-between"
        >
          <span>모델 더 보기</span>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="transform transition-transform {showMoreModels
              ? 'rotate-180'
              : ''}"
          >
            <polyline points="6,9 12,15 18,9" />
          </svg>
        </button>

        {#if showMoreModels}
          <!-- 고급 모델 -->
          <div class="px-2 pb-2">
            <div
              class="px-3 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide"
            >
              고급 모델
            </div>
            {#each advancedModels as model}
              <button
                on:click={() => selectModel(model)}
                class="w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors"
              >
                <span class="text-sm">
                  <span class="text-gray-900 font-medium">{model.provider}</span
                  >
                  <span class="text-gray-500">{model.model}</span>
                </span>
              </button>
            {/each}
          </div>

          <!-- 가벼운 모델 -->
          <div class="px-2 pb-2">
            <div
              class="px-3 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide"
            >
              가벼운 모델
            </div>
            {#each lightModels as model}
              <button
                on:click={() => selectModel(model)}
                class="w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors"
              >
                <span class="text-sm">
                  <span class="text-gray-900 font-medium">{model.provider}</span
                  >
                  <span class="text-gray-500">{model.model}</span>
                </span>
              </button>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>
