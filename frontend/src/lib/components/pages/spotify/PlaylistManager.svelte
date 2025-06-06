<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { api } from "../../../api";
  import { showError, showSuccess } from "../../../stores";
  import LoadingSpinner from "../../ui/LoadingSpinner.svelte";

  const dispatch = createEventDispatcher();

  let loading = false;
  let playlistName = "";
  let playlistDescription = "";
  let isPublic = false;

  async function createPlaylist() {
    if (!playlistName.trim()) {
      showError("플레이리스트 이름을 입력해주세요");
      return;
    }

    try {
      loading = true;

      // 실제 API 호출로 교체
      await api.createSpotifyPlaylist(
        playlistName,
        isPublic,
        playlistDescription
      );

      showSuccess(`플레이리스트 '${playlistName}'이(가) 생성되었습니다!`);

      // 폼 초기화
      playlistName = "";
      playlistDescription = "";
      isPublic = false;

      // 부모 컴포넌트에 알림
      dispatch("playlistCreated");
    } catch (error) {
      console.error("플레이리스트 생성 오류:", error);
      showError("플레이리스트 생성에 실패했습니다");
    } finally {
      loading = false;
    }
  }
</script>

<div class="playlist-manager">
  <div class="header">
    <h3 class="text-xl font-semibold text-white mb-2">
      ➕ 새 플레이리스트 생성
    </h3>
    <p class="text-gray-400 mb-6">새로운 Spotify 플레이리스트를 생성합니다.</p>
  </div>

  <form on:submit|preventDefault={createPlaylist} class="form">
    <div class="input-group">
      <label
        for="playlist-name"
        class="block text-sm font-medium text-gray-300 mb-2"
      >
        플레이리스트 이름 *
      </label>
      <input
        id="playlist-name"
        type="text"
        bind:value={playlistName}
        placeholder="예: 내가 좋아하는 노래들"
        class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        required
      />
    </div>

    <div class="input-group">
      <label
        for="playlist-description"
        class="block text-sm font-medium text-gray-300 mb-2"
      >
        설명 (선택사항)
      </label>
      <textarea
        id="playlist-description"
        bind:value={playlistDescription}
        placeholder="플레이리스트에 대한 설명을 입력하세요..."
        rows="3"
        class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none"
      />
    </div>

    <div class="checkbox-group">
      <label class="flex items-center gap-3">
        <input
          type="checkbox"
          bind:checked={isPublic}
          class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
        />
        <span class="text-gray-300">공개 플레이리스트</span>
      </label>
      <p class="text-sm text-gray-400 mt-1">
        체크하면 다른 사용자들이 이 플레이리스트를 볼 수 있습니다.
      </p>
    </div>

    <div class="actions">
      <button
        type="submit"
        disabled={loading || !playlistName.trim()}
        class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
      >
        {#if loading}
          <LoadingSpinner size="sm" />
          생성 중...
        {:else}
          ✨ 플레이리스트 생성
        {/if}
      </button>
    </div>
  </form>

  <div class="info-box">
    <h4 class="text-sm font-medium text-blue-300 mb-2">💡 팁</h4>
    <ul class="text-sm text-gray-400 space-y-1">
      <li>• 플레이리스트는 생성 후 Spotify 앱에서도 확인할 수 있습니다</li>
      <li>• 생성된 플레이리스트에는 나중에 곡을 추가할 수 있습니다</li>
      <li>• 공개 플레이리스트는 다른 사용자들과 공유됩니다</li>
    </ul>
  </div>
</div>

<style>
  .playlist-manager {
    @apply space-y-6;
  }

  .header {
    @apply border-b border-gray-700 pb-4;
  }

  .form {
    @apply space-y-4;
  }

  .input-group {
    @apply space-y-2;
  }

  .checkbox-group {
    @apply space-y-2;
  }

  .actions {
    @apply pt-4 border-t border-gray-700;
  }

  .info-box {
    @apply bg-blue-900/20 border border-blue-500/30 rounded-lg p-4;
  }
</style>
