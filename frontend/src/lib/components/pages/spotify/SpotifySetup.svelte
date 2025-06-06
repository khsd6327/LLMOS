<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { updateSettings } from "../../../api";
  import { spotifySetupForm, showError, showSuccess } from "../../../stores";
  import LoadingSpinner from "../../ui/LoadingSpinner.svelte";

  const dispatch = createEventDispatcher();

  let loading = false;
  let showSuccessMessage = false;

  // 폼 데이터 반응성
  $: formData = $spotifySetupForm;

  function updateFormData(field: string, value: string) {
    spotifySetupForm.update((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function saveSpotifySettings() {
    if (
      !formData.client_id ||
      !formData.client_secret ||
      !formData.redirect_uri
    ) {
      showError(
        "Client ID, Client Secret, Redirect URI는 반드시 입력해야 합니다."
      );
      return;
    }

    try {
      loading = true;

      // 백엔드 설정 업데이트
      await updateSettings({
        spotify_client_id: formData.client_id,
        spotify_client_secret: formData.client_secret,
        spotify_redirect_uri: formData.redirect_uri,
        spotify_port_type: formData.port_type,
      });

      showSuccessMessage = true;
      showSuccess("Spotify API 설정이 성공적으로 저장되었습니다!");

      // 부모 컴포넌트에 설정 완료 알림
      setTimeout(() => {
        dispatch("configured");
      }, 1500);
    } catch (error) {
      console.error("설정 저장 오류:", error);
      showError("설정 저장 중 오류가 발생했습니다. 다시 시도해주세요.");
    } finally {
      loading = false;
    }
  }

  function closeSuccessMessage() {
    showSuccessMessage = false;
  }
</script>

<div class="setup-container">
  <div class="warning-box">
    <div class="flex items-start gap-3">
      <span class="text-2xl">⚠️</span>
      <div>
        <h3 class="text-lg font-semibold text-yellow-300">
          Spotify API 설정이 필요합니다
        </h3>
        <p class="text-gray-300 mt-1">
          LLMOS에서 Spotify 기능을 사용하려면 API 설정이 필요합니다.
        </p>
      </div>
    </div>
  </div>

  <div class="setup-guide">
    <h3 class="text-xl font-semibold text-white mb-4 flex items-center gap-2">
      🎵 Spotify API 설정
    </h3>

    <div class="guide-content">
      <p class="text-gray-300 mb-4">
        LLMOS에서 Spotify 기능을 사용하려면, Spotify 개발자 대시보드에서
        애플리케이션을 생성하고 다음 정보를 얻어야 합니다:
      </p>

      <ol class="list-decimal list-inside text-gray-300 space-y-2 mb-4">
        <li><strong class="text-white">Client ID</strong></li>
        <li><strong class="text-white">Client Secret</strong></li>
        <li>
          <strong class="text-white">Redirect URI 설정:</strong> 아래 입력한 URI를
          Spotify 앱 설정에 추가해야 합니다.
        </li>
      </ol>

      <a
        href="https://developer.spotify.com/dashboard/"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
      >
        📱 Spotify Developer Dashboard 바로가기
      </a>
    </div>
  </div>

  <div class="form-section">
    <h4 class="text-lg font-semibold text-white mb-4">📝 API 정보 입력</h4>

    <form on:submit|preventDefault={saveSpotifySettings} class="space-y-4">
      <div class="input-group">
        <label
          for="client-id"
          class="block text-sm font-medium text-gray-300 mb-2"
        >
          Spotify Client ID
        </label>
        <input
          id="client-id"
          type="text"
          bind:value={formData.client_id}
          on:input={(e) => updateFormData("client_id", e.target.value)}
          placeholder="Spotify 개발자 대시보드에서 발급받은 Client ID"
          class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          required
        />
      </div>

      <div class="input-group">
        <label
          for="client-secret"
          class="block text-sm font-medium text-gray-300 mb-2"
        >
          Spotify Client Secret
        </label>
        <input
          id="client-secret"
          type="password"
          bind:value={formData.client_secret}
          on:input={(e) => updateFormData("client_secret", e.target.value)}
          placeholder="Spotify 개발자 대시보드에서 발급받은 Client Secret"
          class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          required
        />
      </div>

      <div class="input-group">
        <label
          for="redirect-uri"
          class="block text-sm font-medium text-gray-300 mb-2"
        >
          Spotify Redirect URI
        </label>
        <input
          id="redirect-uri"
          type="url"
          bind:value={formData.redirect_uri}
          on:input={(e) => updateFormData("redirect_uri", e.target.value)}
          placeholder="http://127.0.0.1:8888/callback"
          class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          required
        />
        <p class="text-sm text-gray-400 mt-1">
          Spotify 앱 설정에 등록한 Redirect URI와 정확히 일치해야 합니다.
        </p>
      </div>

      <div class="input-group">
        <label class="block text-sm font-medium text-gray-300 mb-2">
          인증 시 사용할 로컬 포트 타입
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2">
            <input
              type="radio"
              bind:group={formData.port_type}
              value="fixed"
              on:change={() => updateFormData("port_type", "fixed")}
              class="text-blue-500 focus:ring-blue-500"
            />
            <span class="text-gray-300">고정 포트 (예: 8888)</span>
          </label>
          <label class="flex items-center gap-2">
            <input
              type="radio"
              bind:group={formData.port_type}
              value="dynamic"
              on:change={() => updateFormData("port_type", "dynamic")}
              class="text-blue-500 focus:ring-blue-500"
            />
            <span class="text-gray-300">동적 포트 (자동 할당)</span>
          </label>
        </div>
        <p class="text-sm text-gray-400 mt-1">
          대부분의 경우 기본값을 유지해도 괜찮습니다.
        </p>
      </div>

      <button
        type="submit"
        disabled={loading}
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
      >
        {#if loading}
          <LoadingSpinner size="sm" />
        {:else}
          💾
        {/if}
        설정 저장 및 연결
      </button>
    </form>
  </div>

  {#if showSuccessMessage}
    <div class="success-box">
      <div class="flex items-start justify-between">
        <div class="flex items-start gap-3">
          <span class="text-2xl">✅</span>
          <div>
            <h4 class="text-lg font-semibold text-green-300">
              설정 저장 완료!
            </h4>
            <p class="text-gray-300 mt-1">🔄 인증 단계로 자동 이동합니다...</p>
          </div>
        </div>
        <button
          on:click={closeSuccessMessage}
          class="text-gray-400 hover:text-white"
        >
          ❌
        </button>
      </div>
    </div>
  {/if}

  <details class="help-section">
    <summary class="cursor-pointer text-blue-300 hover:text-blue-200 mb-4">
      🤔 설정 방법이 궁금하다면
    </summary>
    <div class="help-content">
      <h4 class="text-lg font-semibold text-white mb-3">
        Spotify 개발자 앱 설정 가이드
      </h4>
      <ol class="list-decimal list-inside text-gray-300 space-y-2">
        <li>
          <strong class="text-white"
            ><a
              href="https://developer.spotify.com/dashboard/"
              target="_blank"
              class="text-blue-400 underline">Spotify Developer Dashboard</a
            ></strong
          > 접속
        </li>
        <li><strong class="text-white">"Create app"</strong> 클릭</li>
        <li>
          앱 정보 입력:
          <ul class="list-disc list-inside ml-6 mt-2 space-y-1">
            <li><strong>App name:</strong> 원하는 이름 (예: "My LLMOS App")</li>
            <li><strong>App description:</strong> 간단한 설명</li>
            <li>
              <strong>Redirect URI:</strong>
              <code class="bg-gray-800 px-2 py-1 rounded"
                >http://127.0.0.1:8888/callback</code
              > 입력
            </li>
            <li><strong>API/SDKs:</strong> Web API 선택</li>
          </ul>
        </li>
        <li>
          생성된 앱에서 <strong class="text-white">Client ID</strong>와
          <strong class="text-white">Client Secret</strong> 복사
        </li>
        <li>위 폼에 입력하고 저장</li>
      </ol>
      <div
        class="mt-4 p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-lg"
      >
        <p class="text-yellow-300">
          💡 <strong>주의사항:</strong> Redirect URI는 정확히 일치해야 합니다!
        </p>
      </div>
    </div>
  </details>
</div>

<style>
  .setup-container {
    @apply max-w-4xl mx-auto space-y-6;
  }

  .warning-box {
    @apply bg-yellow-900/30 border border-yellow-500/30 rounded-lg p-6;
  }

  .setup-guide {
    @apply bg-gray-800 rounded-lg p-6;
  }

  .guide-content {
    @apply space-y-4;
  }

  .form-section {
    @apply bg-gray-800 rounded-lg p-6;
  }

  .input-group {
    @apply space-y-2;
  }

  .success-box {
    @apply bg-green-900/30 border border-green-500/30 rounded-lg p-6;
  }

  .help-section {
    @apply bg-gray-800 rounded-lg p-6;
  }

  .help-content {
    @apply mt-4 space-y-4;
  }

  code {
    @apply bg-gray-700 px-2 py-1 rounded text-sm;
  }
</style>
