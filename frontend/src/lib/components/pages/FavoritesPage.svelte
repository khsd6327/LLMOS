<script lang="ts">
  import { onMount } from "svelte";
  import { favorites, searchQuery, selectedTags } from "$lib/stores";
  import { api } from "$lib/api";
  import { showError, showSuccess } from "$lib/stores";
  import {
    Star,
    Search,
    Filter,
    Trash2,
    Edit,
    Copy,
    MessageSquare,
    Tag,
    Calendar,
    User,
    Bot,
    RefreshCw,
  } from "lucide-svelte";

  let loading = false;
  let filteredFavorites: any[] = [];
  let availableTags: string[] = [];
  let showTagFilter = false;
  let editingFavorite: string | null = null;
  let editNotes = "";

  // 즐겨찾기 목록 로드
  async function loadFavorites() {
    loading = true;
    try {
      const favs = await api.getFavorites();
      favorites.set(favs);

      // 사용 가능한 태그 목록 추출
      const tags = new Set<string>();
      favs.forEach((fav) => {
        fav.tags.forEach((tag) => tags.add(tag));
      });
      availableTags = Array.from(tags).sort();
    } catch (error) {
      console.error("즐겨찾기 로드 실패:", error);
      showError("즐겨찾기를 불러올 수 없습니다.");
    } finally {
      loading = false;
    }
  }

  // 즐겨찾기 필터링
  function filterFavorites() {
    let filtered = $favorites;

    // 검색어로 필터링
    if ($searchQuery.trim()) {
      const query = $searchQuery.toLowerCase();
      filtered = filtered.filter(
        (fav) =>
          fav.content.toLowerCase().includes(query) ||
          (fav.notes && fav.notes.toLowerCase().includes(query)) ||
          fav.tags.some((tag) => tag.toLowerCase().includes(query))
      );
    }

    // 태그로 필터링
    if ($selectedTags.length > 0) {
      filtered = filtered.filter((fav) =>
        $selectedTags.every((tag) => fav.tags.includes(tag))
      );
    }

    filteredFavorites = filtered;
  }

  // 즐겨찾기 삭제
  async function deleteFavorite(favoriteId: string) {
    if (!confirm("이 즐겨찾기를 삭제하시겠습니까?")) return;

    try {
      await api.deleteFavorite(favoriteId);
      favorites.update((list) => list.filter((f) => f.id !== favoriteId));
      showSuccess("즐겨찾기가 삭제되었습니다.");
    } catch (error) {
      console.error("즐겨찾기 삭제 실패:", error);
      showError("즐겨찾기를 삭제할 수 없습니다.");
    }
  }

  // 메모 편집 시작
  function startEditingNotes(favoriteId: string, currentNotes: string) {
    editingFavorite = favoriteId;
    editNotes = currentNotes || "";
  }

  // 메모 편집 저장
  async function saveNotes() {
    if (!editingFavorite) return;

    try {
      const updatedFavorite = await api.updateFavorite(editingFavorite, {
        notes: editNotes.trim(),
      });

      favorites.update((list) =>
        list.map((f) => (f.id === editingFavorite ? updatedFavorite : f))
      );

      showSuccess("메모가 저장되었습니다.");
    } catch (error) {
      console.error("메모 저장 실패:", error);
      showError("메모를 저장할 수 없습니다.");
    }

    editingFavorite = null;
    editNotes = "";
  }

  // 메모 편집 취소
  function cancelEdit() {
    editingFavorite = null;
    editNotes = "";
  }

  // 클립보드 복사
  async function copyToClipboard(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      showSuccess("텍스트가 클립보드에 복사되었습니다.");
    } catch (error) {
      showError("클립보드 복사에 실패했습니다.");
    }
  }

  // 태그 토글
  function toggleTag(tag: string) {
    selectedTags.update((tags) => {
      if (tags.includes(tag)) {
        return tags.filter((t) => t !== tag);
      } else {
        return [...tags, tag];
      }
    });
  }

  // 태그 초기화
  function clearTags() {
    selectedTags.set([]);
  }

  // 반응형 필터링
  $: {
    filterFavorites();
  }

  onMount(() => {
    loadFavorites();
  });

  // 날짜 포맷팅
  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
</script>

<div class="flex-1 overflow-y-auto p-6 space-y-6">
  <!-- 페이지 헤더 -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-dark-100">즐겨찾기</h1>
      <p class="text-dark-400 mt-1">저장한 AI 응답과 대화를 관리하세요.</p>
    </div>

    <button
      class="btn-secondary {loading ? 'animate-spin' : ''}"
      on:click={loadFavorites}
      disabled={loading}
    >
      <RefreshCw size={16} class="mr-2" />
      새로고침
    </button>
  </div>

  <!-- 검색 및 필터 -->
  <div class="card p-4 space-y-4">
    <!-- 검색창 -->
    <div class="relative">
      <Search size={16} class="absolute left-3 top-3 text-dark-400" />
      <input
        type="text"
        placeholder="내용, 태그, 메모에서 검색..."
        bind:value={$searchQuery}
        class="input pl-10"
      />
    </div>

    <!-- 태그 필터 -->
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <button
          class="btn-ghost text-sm"
          on:click={() => (showTagFilter = !showTagFilter)}
        >
          <Filter size={14} class="mr-1" />
          태그 필터 ({$selectedTags.length})
        </button>

        {#if $selectedTags.length > 0}
          <button class="btn-ghost text-xs" on:click={clearTags}>
            모든 태그 해제
          </button>
        {/if}
      </div>

      {#if showTagFilter && availableTags.length > 0}
        <div class="flex flex-wrap gap-2">
          {#each availableTags as tag}
            <button
              class="px-3 py-1 text-xs rounded-full border transition-colors {$selectedTags.includes(
                tag
              )
                ? 'bg-claude-orange text-white border-claude-orange'
                : 'bg-dark-800 text-dark-300 border-dark-600 hover:border-dark-500'}"
              on:click={() => toggleTag(tag)}
            >
              #{tag}
            </button>
          {/each}
        </div>
      {/if}

      <!-- 선택된 태그 표시 -->
      {#if $selectedTags.length > 0}
        <div class="flex flex-wrap gap-2">
          {#each $selectedTags as tag}
            <span
              class="inline-flex items-center px-2 py-1 bg-claude-orange/20 text-claude-orange text-xs rounded-full"
            >
              #{tag}
              <button
                class="ml-1 hover:text-claude-orange/70"
                on:click={() => toggleTag(tag)}
              >
                ×
              </button>
            </span>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- 즐겨찾기 목록 -->
  <div class="space-y-4">
    {#if loading}
      <!-- 로딩 상태 -->
      <div class="flex items-center justify-center py-12">
        <RefreshCw size={32} class="animate-spin text-dark-400" />
      </div>
    {:else if filteredFavorites.length === 0}
      <!-- 빈 상태 -->
      <div class="text-center py-12">
        <Star size={64} class="mx-auto text-dark-600 mb-4" />
        <h3 class="text-lg font-medium text-dark-300 mb-2">
          {$favorites.length === 0
            ? "즐겨찾기가 없습니다"
            : "검색 결과가 없습니다"}
        </h3>
        <p class="text-dark-500 mb-4">
          {$favorites.length === 0
            ? "채팅에서 ⭐ 버튼을 눌러 중요한 응답을 저장하세요."
            : "다른 검색어나 태그를 시도해보세요."}
        </p>
        {#if $searchQuery || $selectedTags.length > 0}
          <button
            class="btn-secondary"
            on:click={() => {
              searchQuery.set("");
              selectedTags.set([]);
            }}
          >
            필터 초기화
          </button>
        {/if}
      </div>
    {:else}
      <!-- 즐겨찾기 아이템들 -->
      {#each filteredFavorites as favorite (favorite.id)}
        <div class="card p-6 space-y-4">
          <!-- 헤더 -->
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-3">
              <!-- 역할 아이콘 -->
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center {favorite.role ===
                'user'
                  ? 'bg-dark-700'
                  : 'bg-gradient-to-br from-claude-orange to-claude-blue'}"
              >
                {#if favorite.role === "user"}
                  <User size={16} class="text-dark-300" />
                {:else}
                  <Bot size={16} class="text-white" />
                {/if}
              </div>

              <!-- 메타데이터 -->
              <div>
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-dark-200">
                    {favorite.role === "user" ? "사용자" : "AI"}
                  </span>
                  {#if favorite.model_name}
                    <span class="text-xs text-dark-500"
                      >• {favorite.model_name}</span
                    >
                  {/if}
                </div>
                <div class="text-xs text-dark-500">
                  {formatDate(favorite.favorited_at)}
                </div>
              </div>
            </div>

            <!-- 액션 버튼 -->
            <div class="flex items-center space-x-2">
              <button
                class="btn-icon"
                on:click={() => copyToClipboard(favorite.content)}
                title="복사"
              >
                <Copy size={14} />
              </button>

              <button
                class="btn-icon"
                on:click={() =>
                  startEditingNotes(favorite.id, favorite.notes || "")}
                title="메모 편집"
              >
                <Edit size={14} />
              </button>

              <button
                class="btn-icon text-red-400 hover:text-red-300"
                on:click={() => deleteFavorite(favorite.id)}
                title="삭제"
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>

          <!-- 메시지 내용 -->
          <div class="prose prose-invert max-w-none text-sm">
            {favorite.content}
          </div>

          <!-- 태그 -->
          {#if favorite.tags.length > 0}
            <div class="flex flex-wrap gap-1">
              {#each favorite.tags as tag}
                <span
                  class="px-2 py-1 bg-dark-700 text-dark-300 text-xs rounded-full"
                >
                  #{tag}
                </span>
              {/each}
            </div>
          {/if}

          <!-- 메모 편집 또는 표시 -->
          {#if editingFavorite === favorite.id}
            <div class="space-y-2">
              <textarea
                bind:value={editNotes}
                placeholder="메모를 입력하세요..."
                class="textarea"
                rows="3"
              />
              <div class="flex justify-end space-x-2">
                <button class="btn-ghost text-sm" on:click={cancelEdit}>
                  취소
                </button>
                <button class="btn-primary text-sm" on:click={saveNotes}>
                  저장
                </button>
              </div>
            </div>
          {:else if favorite.notes}
            <div
              class="bg-dark-800/50 rounded-lg p-3 border-l-4 border-claude-orange"
            >
              <div class="text-xs text-dark-400 mb-1">메모</div>
              <div class="text-sm text-dark-200">{favorite.notes}</div>
            </div>
          {/if}

          <!-- 컨텍스트 메시지 (있는 경우) -->
          {#if favorite.context_messages && favorite.context_messages.length > 1}
            <details class="group">
              <summary
                class="text-xs text-dark-400 cursor-pointer hover:text-dark-300"
              >
                대화 맥락 보기 ({favorite.context_messages.length}개 메시지)
              </summary>
              <div class="mt-3 space-y-2 pl-4 border-l-2 border-dark-700">
                {#each favorite.context_messages as msg}
                  <div class="text-xs">
                    <span class="font-medium text-dark-400">
                      {msg.role === "user" ? "사용자" : "AI"}:
                    </span>
                    <span class="text-dark-500">
                      {msg.content.length > 100
                        ? msg.content.substring(0, 100) + "..."
                        : msg.content}
                    </span>
                  </div>
                {/each}
              </div>
            </details>
          {/if}
        </div>
      {/each}
    {/if}
  </div>

  <!-- 하단 요약 정보 -->
  {#if $favorites.length > 0}
    <div
      class="text-center text-xs text-dark-500 py-4 border-t border-dark-800"
    >
      총 {$favorites.length}개의 즐겨찾기 •
      {filteredFavorites.length}개 표시 중
    </div>
  {/if}
</div>
