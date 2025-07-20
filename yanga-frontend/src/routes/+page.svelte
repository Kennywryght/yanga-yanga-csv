<script lang="ts">
  import { goto } from '$app/navigation';
  import { BACKEND_URL } from '$lib/config';

  export const name = 'Yanga Yanga';

  async function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input?.files?.[0];

    if (!file) {
      alert("No file selected.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${BACKEND_URL}/transactions`, {
        method: "POST",
        body: formData
      });

      const data = await response.json();
      console.log("✅ Upload response:", data);

      if (data.file_id) {
        goto(`/summary/${data.file_id}`);
      } else {
        alert("Upload failed: No file_id returned.");
      }
    } catch (error) {
      console.error("❌ Upload error:", error);
      alert("Something went wrong while uploading.");
    }
  }
</script>

<main class="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-white font-sans">

  <!-- Header with Logo and Search Bar -->
  <header class="flex items-center justify-between px-6 py-4 bg-green-700 text-white">
    <div class="flex items-center space-x-3">
      <img src="/logo.png" alt="Yanga Yanga Logo" class="h-10 w-10 rounded-full object-cover" />
      <span class="text-2xl font-bold tracking-wide">Yanga Yanga</span>
    </div>

    <div class="relative w-64">
      <input
        type="search"
        placeholder="Search transactions..."
        class="w-full rounded-full py-2 px-4 text-gray-800 focus:outline-none focus:ring-2 focus:ring-green-300"
        aria-label="Search transactions"
      />
      <button
        type="submit"
        class="absolute right-2 top-1/2 -translate-y-1/2 text-green-700 hover:text-green-900"
        aria-label="Search"
      >
        🔍
      </button>
    </div>
  </header>

  <!-- Hero Section with File Upload -->
  <section
    class="flex flex-col items-center justify-center text-center py-20 px-4 bg-gradient-to-br from-green-400 to-green-700 text-white"
  >
    <h1 class="text-5xl font-bold mb-4">Take Control of Your Mobile Money</h1>
    <p class="text-xl mb-6">Track, Analyze, and Understand your Airtel/TNM transactions.</p>

    <!-- File Upload Input -->
    <label
      for="fileUpload"
      class="bg-white text-green-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-100 transition cursor-pointer"
    >
      Upload Your CSV File
    </label>
    <input id="fileUpload" type="file" accept=".csv" class="hidden" on:change={handleFileUpload} />
  </section>

  <!-- Features Section -->
  <section
    class="py-16 px-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 bg-gray-50 dark:bg-gray-800"
  >
    <div class="bg-white dark:bg-gray-700 rounded-2xl p-6 shadow-md">
      <h3 class="text-xl font-bold mb-2">📥 Auto Categorization</h3>
      <p>Automatically tags spending like bundles, betting, or bills.</p>
    </div>
    <div class="bg-white dark:bg-gray-700 rounded-2xl p-6 shadow-md">
      <h3 class="text-xl font-bold mb-2">📊 Spend Summary</h3>
      <p>View how much you’ve spent and earned, by category.</p>
    </div>
    <div class="bg-white dark:bg-gray-700 rounded-2xl p-6 shadow-md">
      <h3 class="text-xl font-bold mb-2">🧠 Learns Over Time</h3>
      <p>Yanga Yanga remembers frequent contacts and vendors.</p>
    </div>
    <div class="bg-white dark:bg-gray-700 rounded-2xl p-6 shadow-md">
      <h3 class="text-xl font-bold mb-2">📄 PDF & WhatsApp Reports</h3>
      <p>Download or share summaries easily with others.</p>
    </div>
  </section>

  <!-- How it Works -->
  <section class="py-16 px-6 text-center bg-white dark:bg-gray-900">
    <h2 class="text-3xl font-bold mb-8">How it Works</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div>
        <div class="text-4xl mb-2">📤</div>
        <h4 class="font-bold text-lg mb-1">1. Upload Transaction File</h4>
        <p class="text-sm">Choose your Airtel or TNM CSV file</p>
      </div>
      <div>
        <div class="text-4xl mb-2">⚙️</div>
        <h4 class="font-bold text-lg mb-1">2. Auto-Categorization</h4>
        <p class="text-sm">Yanga Yanga does the magic of tagging your data</p>
      </div>
      <div>
        <div class="text-4xl mb-2">📈</div>
        <h4 class="font-bold text-lg mb-1">3. View & Download Reports</h4>
        <p class="text-sm">Get insights in PDF or share on WhatsApp</p>
      </div>
    </div>
  </section>

  <!-- Call to Action -->
  <section class="py-20 px-6 bg-green-700 text-white text-center">
    <h2 class="text-3xl font-bold mb-4">Ready to understand your spending?</h2>
    <label
      for="fileUploadBottom"
      class="bg-white text-green-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-100 transition cursor-pointer"
    >
      Try Yanga Yanga Now
    </label>
    <input id="fileUploadBottom" type="file" accept=".csv" class="hidden" on:change={handleFileUpload} />
  </section>

  <!-- Footer -->
  <footer
    class="py-6 px-4 text-center bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300"
  >
    <p>&copy; 2025 Yanga Yanga. Made in Malawi 🇲🇼</p>
  </footer>
</main>
