<script lang="ts">
  import { onMount } from "svelte";
  import { api, type SpotifyStatus } from "../../api";
  import {
    spotifyStatus,
    spotifyLoading,
    currentPage,
    showError,
    showSuccess,
  } from "../../stores";
  import LoadingSpinner from "../ui/LoadingSpinner.svelte";
  import SpotifySetup from "./spotify/SpotifySetup.svelte";
  import SpotifyDashboard from "./spotify/SpotifyDashboard.svelte";

  let loading = true;

  onMount(async () => {
    await checkSpotifyStatus();
    loading = false;
  });

  async function checkSpotifyStatus() {
    try {
      spotifyLoading.set(true);
      const status: SpotifyStatus = await api.getSpotifyStatus();
      spotifyStatus.set({
        is_configured: status.is_configured,
        is_authenticated: status.is_authenticated,
        user_id: status.user_id,
      });
    } catch (error) {
      console.error("Spotify 상태 확인 오류:", error);
      showError("Spotify 상태를 확인할 수 없습니다");
    } finally {
      spotifyLoading.set(false);
    }
  }

  function goBackToChat() {
    currentPage.set("chat");
  }

  $: currentSpotifyStatus = $spotifyStatus;
  $: isLoading = $spotifyLoading;
</script>

<div class="spotify-page">
  <div class="header">
    <div class="flex items-center gap-4 mb-6">
      <button
        on:click={goBackToChat}
        class="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
      >
        <span>⬅️</span>
        <span>채팅으로 돌아가기</span>
      </button>

      <div class="flex-1">
        <h1 class="text-3xl font-bold text-white flex items-center gap-3">
          🎵 Spotify 플레이리스트 관리
        </h1>
        <p class="text-gray-400 mt-1">
          Spotify 음악 라이브러리를 관리하고 새로운 음악을 발견하세요.
        </p>
      </div>
    </div>
  </div>

  <div class="content">
    {#if loading}
      <div class="flex justify-center py-12">
        <LoadingSpinner />
      </div>
    {:else if !currentSpotifyStatus?.is_configured}
      <SpotifySetup on:configured={checkSpotifyStatus} />
    {:else if !currentSpotifyStatus?.is_authenticated}
      <div class="auth-section">
        <div
          class="bg-blue-900/30 border border-blue-500/30 rounded-lg p-6 mb-6"
        >
          <h2 class="text-xl font-semibold text-blue-300 mb-2">
            🔐 Spotify 인증이 필요합니다
          </h2>
          <p class="text-gray-300 mb-4">
            설정이 완료되었습니다. 이제 Spotify에 로그인하여 인증을
            완료해주세요.
          </p>

          <button
            on:click={async () => {
              try {
                isLoading = true;
                const result = await api.authenticateSpotify();
                if (result.authenticated) {
                  showSuccess("Spotify 인증이 완료되었습니다!");
                  await checkSpotifyStatus();
                } else {
                  showError(
                    "Spotify 인증에 실패했습니다. 설정을 확인해주세요."
                  );
                }
              } catch (error) {
                console.error("인증 오류:", error);
                showError("인증 중 오류가 발생했습니다");
              } finally {
                isLoading = false;
              }
            }}
            disabled={isLoading}
            class="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            {#if isLoading}
              <LoadingSpinner size="sm" />
            {:else}
              🎵
            {/if}
            Spotify 로그인
          </button>
        </div>
      </div>
    {:else}
      <SpotifyDashboard user_id={currentSpotifyStatus.user_id} />
    {/if}
  </div>
</div>

<style>
  .spotify-page {
    @apply min-h-screen bg-gray-900 text-white p-6;
  }

  .header {
    @apply border-b border-gray-700 pb-6;
  }

  .content {
    @apply pt-6;
  }

  .auth-section {
    @apply max-w-2xl mx-auto;
  }
</style>
