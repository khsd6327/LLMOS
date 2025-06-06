<script lang="ts">
  import { showError, showSuccess } from "../../../stores";
  import LoadingSpinner from "../../ui/LoadingSpinner.svelte";

  export let likedTracks: any[] = [];

  let loading = false;
  let duplicateGroups: any[] = [];
  let tracksToRemove: string[] = [];

  async function findDuplicates() {
    try {
      loading = true;

      // 실제 구현에서는 백엔드 API 호출
      const duplicates = await simulateFindDuplicates();
      duplicateGroups = duplicates;

      if (duplicates.length > 0) {
        showSuccess(`${duplicates.length}개의 중복 그룹을 찾았습니다.`);
      } else {
        showSuccess("중복된 곡이 없습니다.");
      }
    } catch (error) {
      console.error("중복곡 찾기 오류:", error);
      showError("중복곡을 찾는 중 오류가 발생했습니다");
    } finally {
      loading = false;
    }
  }

  async function simulateFindDuplicates() {
    // 실제 API 호출로 교체
    return await api.findSpotifyDuplicates();
  }
    // 실제 구현에서는 백엔드 API 호출
    // 시뮬레이션: 일부 트랙에 대해 중복 그룹 생성
    await new Promise((resolve) => setTimeout(resolve, 2000));

    return [
      [
        {
          id: "1",
          name: "Shape of You",
          artists: "Ed Sheeran",
          added_at: "2023-01-15T10:30:00Z",
          duration_ms: 233713,
        },
        {
          id: "2",
          name: "Shape of You",
          artists: "Ed Sheeran",
          added_at: "2023-06-20T14:22:00Z",
          duration_ms: 233713,
        },
      ],
      [
        {
          id: "3",
          name: "Blinding Lights",
          artists: "The Weeknd",
          added_at: "2023-02-10T09:15:00Z",
          duration_ms: 200040,
        },
        {
          id: "4",
          name: "Blinding Lights",
          artists: "The Weeknd",
          added_at: "2023-08-05T16:45:00Z",
          duration_ms: 200040,
        },
      ],
    ];
  }

  async function removeDuplicates() {
    if (tracksToRemove.length === 0) {
      showError("삭제할 트랙을 선택해주세요");
      return;
    }

    try {
      loading = true;

      // 실제 구현에서는 백엔드 API 호출
      await simulateRemoveTracks();

      showSuccess(`${tracksToRemove.length}개의 중복 트랙을 삭제했습니다.`);
      duplicateGroups = [];
      tracksToRemove = [];
    } catch (error) {
      console.error("트랙 삭제 오류:", error);
      showError("트랙을 삭제하는 중 오류가 발생했습니다");
    } finally {
      loading = false;
    }
  }

  async function simulateRemoveTracks() {
    // 실제 API 호출로 교체
    return await api.removeSpotifyTracks(tracksToRemove);
  }
    // 실제 API 호출로 교체
    return await api.removeSpotifyTracks(tracksToRemove);
  }
    // 실제 구현에서는 백엔드 API 호출
    return new Promise((resolve) => setTimeout(resolve, 1500));
  }

  function toggleTrackSelection(trackId: string) {
    if (tracksToRemove.includes(trackId)) {
      tracksToRemove = tracksToRemove.filter((id) => id !== trackId);
    } else {
      tracksToRemove = [...tracksToRemove, trackId];
    }
  }

  function formatDate(dateString: string): string {
    try {
      const date = new Date(dateString);
      return (
        date.toLocaleDateString("ko-KR") +
        " " +
        date.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" })
      );
    } catch {
      return "날짜 없음";
    }
  }

  function formatDuration(ms: number): string {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  }
</script>

<div class="duplicate-finder">
  <div class="header">
    <h3 class="text-xl font-semibold text-white mb-2">
      👥 좋아요 목록 중복곡 찾기
    </h3>
    <p class="text-gray-400 mb-6">
      곡 이름과 아티스트가 같은 중복된 트랙을 찾습니다.
    </p>
  </div>

  <div class="search-section">
    <button
      on:click={findDuplicates}
      disabled={loading}
      class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
    >
      {#if loading && duplicateGroups.length === 0}
        <LoadingSpinner size="sm" />
        중복곡 검색 중...
      {:else}
        🔍 중복곡 찾기
      {/if}
    </button>
  </div>

  {#if duplicateGroups.length > 0}
    <div class="results">
      <div class="results-header">
        <h4 class="text-lg font-semibold text-white">검색 결과</h4>
        <p class="text-gray-400">
          {duplicateGroups.length}개의 중복 그룹을 찾았습니다
        </p>
      </div>

      <div class="duplicate-groups">
        {#each duplicateGroups as group, groupIndex}
          {#if group.length >= 2}
            <div class="duplicate-group">
              <div class="group-header">
                <h5 class="font-medium text-white">
                  {groupIndex + 1}. {group[0].name} - {group[0].artists.split(
                    ","
                  )[0]} ({group.length}개)
                </h5>
              </div>

              <div class="tracks">
                {#each group.sort( (a, b) => (a.added_at || "").localeCompare(b.added_at || "") ) as track, trackIndex}
                  <div class="track-item">
                    <div class="track-selection">
                      {#if trackIndex === 0}
                        <span class="keep-label">유지</span>
                      {:else}
                        <label class="flex items-center">
                          <input
                            type="checkbox"
                            checked={tracksToRemove.includes(track.id)}
                            on:change={() => toggleTrackSelection(track.id)}
                            class="w-4 h-4 text-red-600 rounded focus:ring-red-500"
                          />
                          <span class="ml-2 text-red-400">삭제</span>
                        </label>
                      {/if}
                    </div>

                    <div class="track-info">
                      <div class="track-details">
                        <span class="text-gray-300"
                          >추가: {formatDate(track.added_at)}</span
                        >
                      </div>
                      <div class="track-meta">
                        <span class="text-gray-400"
                          >길이: {formatDuration(track.duration_ms)}</span
                        >
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        {/each}
      </div>

      {#if tracksToRemove.length > 0}
        <div class="actions">
          <div class="warning">
            <span class="text-yellow-300">⚠️</span>
            <span class="text-gray-300">
              {tracksToRemove.length}개의 트랙이 선택되었습니다. 삭제하면 되돌릴
              수 없습니다!
            </span>
          </div>

          <button
            on:click={removeDuplicates}
            disabled={loading}
            class="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
          >
            {#if loading && tracksToRemove.length > 0}
              <LoadingSpinner size="sm" />
              삭제 중...
            {:else}
              🗑️ 선택한 {tracksToRemove.length}개 트랙 삭제
            {/if}
          </button>
        </div>
      {:else}
        <div class="info">
          <p class="text-gray-400">삭제할 트랙을 선택해주세요.</p>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .duplicate-finder {
    @apply space-y-6;
  }

  .header {
    @apply border-b border-gray-700 pb-4;
  }

  .search-section {
    @apply space-y-4;
  }

  .results {
    @apply space-y-6;
  }

  .results-header {
    @apply border-b border-gray-700 pb-3;
  }

  .duplicate-groups {
    @apply space-y-4;
  }

  .duplicate-group {
    @apply bg-gray-700 rounded-lg p-4 space-y-3;
  }

  .group-header {
    @apply border-b border-gray-600 pb-2;
  }

  .tracks {
    @apply space-y-2;
  }

  .track-item {
    @apply flex items-center gap-4 p-3 bg-gray-600 rounded-lg;
  }

  .track-selection {
    @apply flex-shrink-0 w-16;
  }

  .keep-label {
    @apply text-green-400 font-medium text-sm;
  }

  .track-info {
    @apply flex-1 space-y-1;
  }

  .track-details {
    @apply text-sm;
  }

  .track-meta {
    @apply text-xs;
  }

  .actions {
    @apply space-y-4 pt-6 border-t border-gray-700;
  }

  .warning {
    @apply flex items-center gap-2 p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-lg;
  }

  .info {
    @apply text-center py-4;
  }
</style>
