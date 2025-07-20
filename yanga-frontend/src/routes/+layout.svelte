<script lang="ts">
  import { page } from '$app/stores';
  import '../app.css';

  let sidebarOpen = false;

  const links = [
    { href: '/', label: '🏠 Home' },
    { href: '/upload', label: '📤 Upload' },
    { href: '/transactions', label: '📄 Transactions' },
    { href: '/summary', label: '📊 Summary' }
  ];

  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }

  function closeSidebar() {
    sidebarOpen = false;
  }
</script>

<!-- OUTER WRAPPER -->
<div class="relative h-screen flex flex-col bg-gray-100 dark:bg-gray-900">

  <!-- ✅ TOP BAR -->
  <header class="bg-white dark:bg-gray-800 shadow-md flex items-center justify-between px-4 py-3">
    <div class="flex items-center gap-3">
      <button class="text-green-700 dark:text-green-300 text-2xl" on:click={toggleSidebar} aria-label="Open menu">
        ☰
      </button>
      <h1 class="text-lg font-semibold text-gray-700 dark:text-gray-200">Yanga Yanga</h1>
    </div>
  </header>

  <!-- ✅ SIDEBAR (Drawer Style) -->
  <div class={`fixed top-0 left-0 h-full w-64 bg-green-700 text-white transform transition-transform duration-300 ease-in-out z-50 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
    <div class="flex items-center justify-between p-4 border-b border-green-600">
      <div class="flex items-center gap-2">
        <img src="/logo.png" alt="Logo" class="h-8 w-8 rounded-full" />
        <h2 class="text-lg font-bold">Yanga Yanga</h2>
      </div>
      <button class="text-white text-lg" on:click={closeSidebar} aria-label="Close menu">
        ✖
      </button>
    </div>

    <nav class="flex flex-col gap-2 p-4">
      {#each links as { href, label }}
        <a
          href={href}
          class="px-4 py-2 rounded-md hover:bg-green-800 transition
          {($page.url.pathname === href || $page.url.pathname.startsWith(href + '/')) ? 'bg-green-900 text-yellow-300' : ''}"
          on:click={closeSidebar}
        >
          {label}
        </a>
      {/each}
    </nav>

    <div class="absolute bottom-4 w-full text-center text-xs opacity-70 text-green-100">
      &copy; {new Date().getFullYear()} Yanga Yanga — Malawi 🇲🇼
    </div>
  </div>

  <!-- ✅ PAGE CONTENT -->
  <main class="flex-1 overflow-auto p-4 sm:p-6 md:p-8 text-gray-900 dark:text-gray-100">
    <slot />
  </main>
</div>
