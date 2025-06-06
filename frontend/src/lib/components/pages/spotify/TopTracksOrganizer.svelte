<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { api } from "../../../api";
  import { showError, showSuccess } from "../../../stores";
  import LoadingSpinner from "../../ui/LoadingSpinner.svelte";

  export let playlists: any[] = [];

  const dispatch = createEventDispatcher();

  let loading = false;
  let tasks: any[] = [];
  let clearExisting = true;

  // 플레이리스트 옵션 (새 플레이리스트 생성 포함)
  $: playlistOptions = [
    "새 플레이리스트 생성",
    ...playlists.map((p) => p.name),
  ];

  // 작업 설정
  let longTermEnabled = true;
  let longTermPlaylist = "새 플레이리스트 생성";
  let longTermNewName = "절대적 최애곡";

  let frequentEnabled = true;
  let frequentPlaylist = "새 플레이리스트 생성";
  let frequentNewName = "자주 듣는 곡";

  let shortTermEnabled = true;
  let shortTermPlaylist = "새 플레이리스트 생성";
  let shortTermNewName = "요즘 최고야";

  function buildTasks() {
    tasks = [];

    if (longTermEnabled) {
      tasks.push({
        type: "long_term",
        playlist_id:
          longTermPlaylist === "새 플레이리스트 생성"
            ? null
            : playlists.find((p) => p.name === longTermPlaylist)?.id,
        playlist_name:
          longTermPlaylist === "새 플레이리스트 생성"
            ? longTermNewName
            : longTermPlaylist,
        create_new: longTermPlaylist === "새 플레이리스트 생성",
      });
    }

    if (frequentEnabled) {
      tasks.push({
        type: "frequent",
        playlist_id:
          frequentPlaylist === "새 플레이리스트 생성"
            ? null
            : playlists.find((p) => p.name === frequentPlaylist)?.id,
        playlist_name:
          frequentPlaylist === "새 플레이리스트 생성"
            ? frequentNewName
            : frequentPlaylist,
        create_new: frequentPlaylist === "새 플레이리스트 생성",
      });
    }

    if (shortTermEnabled) {
      tasks.push({
        type: "short_term",
        playlist_id:
          shortTermPlaylist === "새 플레이리스트 생성"
            ? null
            : playlists.find((p) => p.name === shortTermPlaylist)?.id,
        playlist_name:
          shortTermPlaylist === "새 플레이리스트 생성"
            ? shortTermNewName
            : shortTermPlaylist,
        create_new: shortTermPlaylist === "새 플레이리스트 생성",
      });
    }
  }

  async function startOrganization() {
    buildTasks();

    if (tasks.length === 0) {
      showError("최소 하나의 정리 옵션을 선택해주세요");
      return;
    }

    try {
      loading = true;

      // 실제 API 호출로 교체
      await api.organizeSpotifyTopTracks(tasks, clearExisting);

      showSuccess("Top 트랙 정리가 완료되었습니다!");
      dispatch("completed");
    } catch (error) {
      console.error("Top 트랙 정리 오류:", error);
      showError("Top 트랙 정리 중 오류가 발생했습니다");
    } finally {
      loading = false;
    }
  }
</script>

<div class="organizer">
  <div class="header">
    <h3 class="text-xl font-semibold text-white mb-2">
      🎯 Top 트랙 플레이리스트 정리
    </h3>
    <p class="text-gray-400 mb-6">
      자주 듣는 곡들을 자동으로 플레이리스트로 정리합니다.
    </p>
  </div>

  <div class="options">
    <h4 class="text-lg font-medium text-white mb-4">정리 옵션 선택</h4>

    <!-- 절대적 최애곡 -->
    <div class="option-group">
      <div class="option-header">
        <label class="flex items-center gap-3">
          <input
            type="checkbox"
            bind:checked={longTermEnabled}
            class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span class="text-white font-medium">절대적 최애곡</span>
        </label>
      </div>

      {#if longTermEnabled}
        <div class="option-content">
          <select
            bind:value={longTermPlaylist}
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            {#each playlistOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>

          {#if longTermPlaylist === "새 플레이리스트 생성"}
            <input
              type="text"
              bind:value={longTermNewName}
              placeholder="새 플레이리스트 이름"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
            />
          {/if}
        </div>
      {/if}
    </div>

    <!-- 자주 듣는 곡 -->
    <div class="option-group">
      <div class="option-header">
        <label class="flex items-center gap-3">
          <input
            type="checkbox"
            bind:checked={frequentEnabled}
            class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span class="text-white font-medium">자주 듣는 곡</span>
        </label>
      </div>

      {#if frequentEnabled}
        <div class="option-content">
          <select
            bind:value={frequentPlaylist}
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            {#each playlistOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>

          {#if frequentPlaylist === "새 플레이리스트 생성"}
            <input
              type="text"
              bind:value={frequentNewName}
              placeholder="새 플레이리스트 이름"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
            />
          {/if}
        </div>
      {/if}
    </div>

    <!-- 요즘 최고야 -->
    <div class="option-group">
      <div class="option-header">
        <label class="flex items-center gap-3">
          <input
            type="checkbox"
            bind:checked={shortTermEnabled}
            class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span class="text-white font-medium">요즘 최고야!</span>
        </label>
      </div>

      {#if shortTermEnabled}
        <div class="option-content">
          <select
            bind:value={shortTermPlaylist}
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            {#each playlistOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>

          {#if shortTermPlaylist === "새 플레이리스트 생성"}
            <input
              type="text"
              bind:value={shortTermNewName}
              placeholder="새 플레이리스트 이름"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
            />
          {/if}
        </div>
      {/if}
    </div>
  </div>

  <div class="settings">
    <label class="flex items-center gap-3">
      <input
        type="checkbox"
        bind:checked={clearExisting}
        class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
      />
      <span class="text-gray-300">기존 곡 삭제 후 새로 채우기</span>
    </label>
  </div>

  <div class="actions">
    <button
      on:click={startOrganization}
      disabled={loading || tasks.length === 0}
      class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
    >
      {#if loading}
        <LoadingSpinner size="sm" />
        정리 중...
      {:else}
        🚀 정리 시작
      {/if}
    </button>
  </div>
</div>

<style>
  .organizer {
    @apply space-y-6;
  }

  .header {
    @apply border-b border-gray-700 pb-4;
  }

  .options {
    @apply space-y-4;
  }

  .option-group {
    @apply bg-gray-700 rounded-lg p-4 space-y-3;
  }

  .option-header {
    @apply flex items-center justify-between;
  }

  .option-content {
    @apply space-y-3;
  }

  .settings {
    @apply bg-gray-700 rounded-lg p-4;
  }

  .actions {
    @apply pt-4 border-t border-gray-700;
  }
</style>
