<script lang="ts">
  import { BACKEND_URL } from '$lib/config';
  import { goto } from '$app/navigation';

  let file: File | null = null;
  let fileInput: HTMLInputElement | null = null;
  let uploading = false;
  let uploadProgress = 0;
  let csvPreview: string[][] = [];
  let errorMessage = '';
  let isDragOver = false;

  function parseCSV(text: string): string[][] {
    return text
      .trim()
      .split('\n')
      .map(line => line.split(',').map(cell => cell.trim()));
  }

  async function loadCSVPreview(file: File) {
    try {
      const text = await file.text();
      csvPreview = parseCSV(text).slice(0, 10);
      errorMessage = '';
    } catch {
      csvPreview = [];
      errorMessage = 'Failed to parse CSV preview.';
    }
  }

  function selectFile(newFile: File) {
    if (newFile.type !== 'text/csv' && !newFile.name.endsWith('.csv')) {
      alert('Please select a valid CSV file.');
      return;
    }
    file = newFile;
    loadCSVPreview(newFile);
  }

  function onDragOver(event: DragEvent) {
    event.preventDefault();
    isDragOver = true;
  }

  function onDragLeave(event: DragEvent) {
    event.preventDefault();
    isDragOver = false;
  }

  function onDrop(event: DragEvent) {
    event.preventDefault();
    isDragOver = false;
    if (event.dataTransfer?.files.length) {
      selectFile(event.dataTransfer.files[0]);
      if (fileInput) fileInput.value = '';
    }
  }

  async function handleUpload() {
    if (!file) {
      alert('Please select a file to upload');
      return;
    }

    uploading = true;
    uploadProgress = 0;
    errorMessage = '';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${BACKEND_URL}/transactions`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      uploading = false;

      if (response.ok && data?.file_id) {
        // ✅ Redirect to summary with query param
        goto(`/summary?file_id=${data.file_id}`);
      } else {
        errorMessage = 'Upload succeeded but no file ID returned.';
        console.error('Missing file_id in response:', data);
      }
    } catch (err) {
      uploading = false;
      errorMessage = 'Network or server error during upload.';
      console.error(err);
    }
  }

  function resetForm() {
    file = null;
    csvPreview = [];
    uploadProgress = 0;
    errorMessage = '';
    if (fileInput) fileInput.value = '';
  }
</script>

<style>
  .dragover {
    border-color: #22c55e;
    background-color: #dcfce7;
  }

  .spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #22c55e;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    animation: spin 1s linear infinite;
    margin: 0 auto;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>

<main class="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-white font-sans flex flex-col">
  <section class="flex-grow flex flex-col items-center justify-center p-6 max-w-3xl mx-auto w-full">
    <h2 class="text-3xl font-bold mb-8">Upload Your Transaction File</h2>

    <div
      class="w-full border-4 border-dashed rounded-xl p-10 mb-6 text-center cursor-pointer transition-colors
             border-gray-300 dark:border-gray-700 {isDragOver ? 'dragover' : ''}"
      on:dragover={onDragOver}
      on:dragleave={onDragLeave}
      on:drop={onDrop}
      on:click={() => fileInput?.click()}
      tabindex="0"
      role="button"
      on:keydown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          fileInput?.click();
        }
      }}
    >
      <p class="text-gray-500 dark:text-gray-400">
        {#if file}
          Selected file: <strong>{file.name}</strong><br />
          Drag & drop to replace or click here to select a different file.
        {:else}
          Drag & drop your CSV file here, or click to select.
        {/if}
      </p>

      <input
        type="file"
        bind:this={fileInput}
        accept=".csv"
        class="hidden"
        on:change={(e: Event) => {
          const target = e.target as HTMLInputElement;
          if (target.files && target.files.length > 0) {
            selectFile(target.files[0]);
          }
        }}
      />
    </div>

    {#if csvPreview.length}
      <div class="overflow-auto w-full mb-6 rounded-lg shadow-md border border-gray-300 dark:border-gray-700">
        <table class="min-w-full table-auto border-collapse text-sm text-left text-gray-900 dark:text-gray-100">
          <thead class="bg-green-600 text-white">
            <tr>
              {#each csvPreview[0] as header}
                <th class="px-4 py-2 border border-green-700">{header}</th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each csvPreview.slice(1) as row}
              <tr class="odd:bg-gray-50 even:bg-white dark:odd:bg-gray-800 dark:even:bg-gray-900">
                {#each row as cell}
                  <td class="px-4 py-2 border border-green-700">{cell}</td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}

    {#if errorMessage}
      <p class="mb-4 text-red-600 dark:text-red-400">{errorMessage}</p>
    {/if}

    {#if uploading}
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 mb-4 overflow-hidden">
        <div
          class="bg-green-600 h-4 transition-all duration-300"
          style="width: {uploadProgress}%"
          role="progressbar"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={uploadProgress}
        ></div>
      </div>
      <div class="mb-6 flex flex-col items-center">
        <div class="spinner mb-2"></div>
        <p class="text-green-700 dark:text-green-400 font-semibold">{uploadProgress}% uploading...</p>
      </div>
    {/if}

    <div class="flex space-x-4 w-full max-w-xs">
      <button
        class="flex-grow bg-green-700 hover:bg-green-800 text-white font-semibold py-3 rounded-xl transition disabled:opacity-50 disabled:cursor-not-allowed"
        on:click={handleUpload}
        disabled={!file || uploading}
      >
        Upload
      </button>
      <button
        class="bg-gray-400 hover:bg-gray-500 text-gray-900 font-semibold py-3 px-6 rounded-xl transition"
        on:click={resetForm}
        disabled={uploading && !file}
      >
        Reset
      </button>
    </div>
  </section>

  <footer class="py-6 px-4 text-center bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
    <p>&copy; 2025 Yanga Yanga. Made in Malawi 🇲🇼</p>
  </footer>
</main>
