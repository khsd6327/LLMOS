<script lang="ts">
    import { showError, showSuccess } from '../../../stores';
    import LoadingSpinner from '../../ui/LoadingSpinner.svelte';
  
    export let likedTracks: any[] = [];
  
    let loading = false;
    let cleanupCandidates: any[] = [];
    let totalLiked = 0;
    let candidateCount = 50;
    let tracksToRemove: string[] = [];
    let selectAll = false;
  
    async function findCleanupCandidates() {
      try {
        loading = true;
        
        // 실제 구현에서는 백엔드 API 호출
        const { candidates, total } = await simulateFindCandidates();
        cleanupCandidates = candidates;
        totalLiked = total;
        
        if (candidates.length > 0) {
          showSuccess(`총 ${total}개 중 ${candidates.length}개의 정리 후보를 찾았습니다.`);
        } else {
          showSuccess('정리할 후보 곡이 없습니다.');
        }
        
      } catch (error) {
        console.error('정리 후보 찾기 오류:', error);
        showError('정리 후보를 찾는 중 오류가 발생했습니다');
      } finally {
        loading = false;
      }
    }
  
    async function simulateFindCandidates() {
    // 실제 API 호출로 교체
    const result = await api.getSpotifyOldTracks(candidateCount);
    return { candidates: result.tracks, total: result.total };
  }
      // 실제 구현에서는 백엔드 API 호출
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const candidates = [
        { id: '1', name: 'Old Song 1', artists: 'Artist A', added_at: '2020-01-15T10:30:00Z' },
        { id: '2', name: 'Old Song 2', artists: 'Artist B', added_at: '2019-06-20T14:22:00Z' },
        { id: '3', name: 'Old Song 3', artists: 'Artist C', added_at: '2018-02-10T09:15:00Z' },
        { id: '4', name: 'Old Song 4', artists: 'Artist D', added_at: '2017-08-05T16:45:00Z' },
        { id: '5', name: 'Old Song 5', artists: 'Artist E', added_at: '2016-12-25T12:00:00Z' }
      ].slice(0, candidateCount);
      
      return { candidates, total: likedTracks.length || 1500 };
    }
  
    async function removeSelectedTracks() {
      if (tracksToRemove.length === 0) {
        showError('삭제할 트랙을 선택해주세요');
        return;
      }
  
      try {
        loading = true;
        
        // 실제 구현에서는 백엔드 API 호출
        await simulateRemoveTracks();
        
        showSuccess(`${tracksToRemove.length}개의 트랙을 삭제했습니다.`);
        cleanupCandidates = [];
        tracksToRemove = [];
        selectAll = false;
        
      } catch (error) {
        console.error('트랙 삭제 오류:', error);
        showError('트랙을 삭제하는 중 오류가 발생했습니다');
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
      return new Promise(resolve => setTimeout(resolve, 1500));
    }
  
    function toggleTrackSelection(trackId: string) {
      if (tracksToRemove.includes(trackId)) {
        tracksToRemove = tracksToRemove.filter(id => id !== trackId);
      } else {
        tracksToRemove = [...tracksToRemove, trackId];
      }
    }
  
    function handleSelectAll() {
      if (selectAll) {
        tracksToRemove = cleanupCandidates.map(track => track.id);
      } else {
        tracksToRemove = [];
      }
    }
  
    function formatDate(dateString: string): string {
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR');
      } catch {
        return '날짜 없음';
      }
    }
  
    $: {
      handleSelectAll();
    }
  </script>
  
  <div class="cleanup-tools">
    <div class="header">
      <h3 class="text-xl font-semibold text-white mb-2">🧹 오래된 좋아요 곡 정리</h3>
      <p class="text-gray-400 mb-6">
        최근에 듣지 않는 오래된 곡들을 찾아 정리합니다.
      </p>
    </div>
  
    <div class="settings">
      <div class="input-group">
        <label for="candidate-count" class="block text-sm font-medium text-gray-300 mb-2">
          조회할 후보 곡 수
        </label>
        <input
          id="candidate-count"
          type="number"
          bind:value={candidateCount}
          min="10"
          max="200"
          step="10"
          class="w-32 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
        />
      </div>
  
      <button
        on:click={findCleanupCandidates}
        disabled={loading}
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
      >
        {#if loading && cleanupCandidates.length === 0}
          <LoadingSpinner size="sm" />
          정리 후보 곡 분석 중...
        {:else}
          🔍 정리 후보 곡 찾기
        {/if}
      </button>
    </div>
  
    {#if cleanupCandidates.length > 0}
      <div class="results">
        <div class="results-header">
          <h4 class="text-lg font-semibold text-white">
            정리 후보 곡 (총 좋아요: {totalLiked}개)
          </h4>
          
          <div class="select-all">
            <label class="flex items-center gap-2">
              <input
                type="checkbox"
                bind:checked={selectAll}
                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span class="text-gray-300">전체 선택</span>
            </label>
          </div>
        </div>
  
        <div class="candidates">
          {#each cleanupCandidates as track}
            <div class="candidate-item">
              <div class="track-selection">
                <label class="flex items-center">
                  <input
                    type="checkbox"
                    checked={tracksToRemove.includes(track.id)}
                    on:change={() => toggleTrackSelection(track.id)}
                    class="w-4 h-4 text-red-600 rounded focus:ring-red-500"
                  />
                  <span class="ml-2 text-red-400">삭제</span>
                </label>
              </div>
  
              <div class="track-info">
                <div class="track-title">
                  <h5 class="font-medium text-white">{track.name}</h5>
                  <p class="text-gray-400 text-sm">{track.artists}</p>
                </div>
              </div>
  
              <div class="track-meta">
                <span class="text-gray-400 text-sm">
                  추가: {formatDate(track.added_at)}
                </span>
              </div>
            </div>
          {/each}
        </div>
  
        {#if tracksToRemove.length > 0}
          <div class="actions">
            <div class="warning">
              <span class="text-yellow-300">⚠️</span>
              <span class="text-gray-300">
                {tracksToRemove.length}개의 트랙이 선택되었습니다. 삭제하면 되돌릴 수 없습니다!
              </span>
            </div>
            
            <div class="confirmation">
              <label class="flex items-center gap-2">
                <input
                  type="checkbox"
                  bind:checked={confirmDelete}
                  class="w-4 h-4 text-red-600 rounded focus:ring-red-500"
                />
                <span class="text-gray-300">정말로 삭제하시겠습니까?</span>
              </label>
            </div>
            
            <button
              on:click={removeSelectedTracks}
              disabled={loading || !confirmDelete}
              class="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              {#if loading && tracksToRemove.length > 0}
                <LoadingSpinner size="sm" />
                삭제 중...
              {:else}
                🗑️ 선택한 {tracksToRemove.length}개 트랙 영구 삭제
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
  
  <script>
    let confirmDelete = false;
  </script>
  
  <style>
    .cleanup-tools {
      @apply space-y-6;
    }
  
    .header {
      @apply border-b border-gray-700 pb-4;
    }
  
    .settings {
      @apply space-y-4;
    }
  
    .input-group {
      @apply space-y-2;
    }
  
    .results {
      @apply space-y-6;
    }
  
    .results-header {
      @apply flex items-center justify-between border-b border-gray-700 pb-3;
    }
  
    .select-all {
      @apply flex items-center;
    }
  
    .candidates {
      @apply space-y-2;
    }
  
    .candidate-item {
      @apply flex items-center gap-4 p-3 bg-gray-700 rounded-lg;
    }
  
    .track-selection {
      @apply flex-shrink-0 w-16;
    }
  
    .track-info {
      @apply flex-1;
    }
  
    .track-title {
      @apply space-y-1;
    }
  
    .track-meta {
      @apply flex-shrink-0;
    }
  
    .actions {
      @apply space-y-4 pt-6 border-t border-gray-700;
    }
  
    .warning {
      @apply flex items-center gap-2 p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-lg;
    }
  
    .confirmation {
      @apply p-3 bg-red-900/30 border border-red-500/30 rounded-lg;
    }
  
    .info {
      @apply text-center py-4;
    }
  </style>