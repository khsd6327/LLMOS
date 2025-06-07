<script lang="ts">
  import Modal from "../../ui/overlay/Modal.svelte";
  import {
    settingsModal,
    settingsModalActions,
    settings,
  } from "../../../stores/settings/index.js";

  // 모달 닫기
  function handleClose() {
    settingsModalActions.close();
  }

  // 임시 탭 메뉴 (Phase 2에서 실제 콘텐츠 구현)
  const tabs = [
    { id: "models", name: "AI 모델", icon: "🤖" },
    { id: "api-keys", name: "API 키", icon: "🔑" },
    { id: "interface", name: "인터페이스", icon: "🎨" },
    { id: "advanced", name: "고급", icon: "⚙️" },
  ] as const;

  function selectTab(tabId: (typeof tabs)[number]["id"]) {
    settingsModalActions.setTab(tabId);
  }
</script>

<Modal
  isOpen={$settingsModal.isOpen}
  title="설정"
  size="lg"
  on:close={handleClose}
>
  <div class="flex h-96">
    <!-- 왼쪽 탭 메뉴 -->
    <div class="w-48 border-r border-gray-200 p-4">
      <nav class="space-y-2">
        {#each tabs as tab}
          <button
            class="w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center space-x-2
                     {$settingsModal.currentTab === tab.id
              ? 'bg-blue-100 text-blue-700'
              : 'hover:bg-gray-100'}"
            on:click={() => selectTab(tab.id)}
          >
            <span>{tab.icon}</span>
            <span class="text-sm font-medium">{tab.name}</span>
          </button>
        {/each}
      </nav>
    </div>

    <!-- 오른쪽 콘텐츠 영역 -->
    <div class="flex-1 p-6">
      {#if $settingsModal.isLoading}
        <div class="flex items-center justify-center h-full">
          <div class="text-gray-500">설정을 불러오는 중...</div>
        </div>
      {:else if $settingsModal.error}
        <div class="flex items-center justify-center h-full">
          <div class="text-red-500">오류: {$settingsModal.error}</div>
        </div>
      {:else}
        <!-- 탭별 콘텐츠 (Phase 2에서 구현) -->
        {#if $settingsModal.currentTab === "models"}
          <div>
            <h3 class="text-lg font-semibold mb-4">AI 모델 설정</h3>
            <p class="text-gray-600">
              AI 모델 설정 기능을 곧 구현할 예정입니다.
            </p>
          </div>
        {:else if $settingsModal.currentTab === "api-keys"}
          <div>
            <h3 class="text-lg font-semibold mb-4">API 키 관리</h3>
            <p class="text-gray-600">
              API 키 관리 기능을 곧 구현할 예정입니다.
            </p>
          </div>
        {:else if $settingsModal.currentTab === "interface"}
          <div>
            <h3 class="text-lg font-semibold mb-4">인터페이스 설정</h3>
            <p class="text-gray-600">
              인터페이스 설정 기능을 곧 구현할 예정입니다.
            </p>
          </div>
        {:else if $settingsModal.currentTab === "advanced"}
          <div>
            <h3 class="text-lg font-semibold mb-4">고급 설정</h3>
            <p class="text-gray-600">고급 설정 기능을 곧 구현할 예정입니다.</p>
          </div>
        {/if}
      {/if}
    </div>
  </div>

  <!-- 푸터 -->
  <div slot="footer" class="flex justify-end space-x-3">
    <button
      class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
      on:click={handleClose}
    >
      취소
    </button>
    <button
      class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors
               {$settingsModal.isSaving ? 'opacity-50 cursor-not-allowed' : ''}"
      disabled={$settingsModal.isSaving}
    >
      {$settingsModal.isSaving ? "저장 중..." : "저장"}
    </button>
  </div>
</Modal>
