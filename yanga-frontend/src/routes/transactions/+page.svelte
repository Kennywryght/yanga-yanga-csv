<script lang="ts">
  import { onMount } from 'svelte';
  import { BACKEND_URL } from '$lib/config';

  type Transaction = {
    id: string;
    file_id: string;
    details: string;
    amount: number;
    category: string;
    timestamp: string; // ISO string
    needs_confirmation?: boolean; // ✅ Added this
  };

  let transactions: Transaction[] = [];
  let loading: boolean = true;
  let error: string | null = null;
  let search: string = "";
  let selectedCategory: string = "All";

  $: filteredTransactions = transactions.filter(txn => {
    const matchesSearch = txn.details.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === "All" || txn.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  $: categories = ["All", ...new Set(transactions.map(t => t.category))];

  $: totalIncome = transactions
    .filter(t => t.amount > 0)
    .reduce((sum, t) => sum + t.amount, 0);

  $: totalSpent = transactions
    .filter(t => t.amount < 0)
    .reduce((sum, t) => sum + Math.abs(t.amount), 0);

  onMount(async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/transactions`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      // ✅ Support both raw array and { transactions: [...] }
      transactions = Array.isArray(data) ? data : data.transactions;
    } catch (err: unknown) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loading = false;
    }
  });

  function formatDate(dateStr: string): string {
    try {
      const parsed = new Date(dateStr);
      if (isNaN(parsed.getTime())) return "Invalid Date";
      return parsed.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return "Invalid Date";
    }
  }

  function downloadCSV() {
    const headers = ['Date', 'Details', 'Amount', 'Category'];
    const rows = filteredTransactions.map(t =>
      [formatDate(t.timestamp), t.details, t.amount, t.category]
    );
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transactions.csv';
    a.click();
    URL.revokeObjectURL(url);
  }
</script>

<!-- ✅ FILTERS -->
<section class="p-6 flex flex-col sm:flex-row gap-4 bg-gray-100">
  <input
    type="text"
    placeholder="🔍 Search details..."
    bind:value={search}
    class="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-green-500"
  />
  <select
    bind:value={selectedCategory}
    class="px-4 py-2 rounded-lg border border-gray-300 focus:ring-green-500"
  >
    {#each categories as cat}
      <option value={cat}>{cat}</option>
    {/each}
  </select>
</section>

<!-- ✅ DASHBOARD SUMMARY -->
<section class="p-6 grid grid-cols-1 md:grid-cols-3 gap-6 bg-white">
  <div class="bg-green-100 text-green-800 p-6 rounded-xl text-center shadow">
    <p>Total Income</p>
    <h2 class="text-3xl font-bold mt-2">+{totalIncome.toLocaleString()} MWK</h2>
  </div>
  <div class="bg-red-100 text-red-800 p-6 rounded-xl text-center shadow">
    <p>Total Spent</p>
    <h2 class="text-3xl font-bold mt-2">-{totalSpent.toLocaleString()} MWK</h2>
  </div>
  <div class="bg-indigo-100 text-indigo-800 p-6 rounded-xl text-center shadow">
    <p>Total Transactions</p>
    <h2 class="text-3xl font-bold mt-2">{transactions.length}</h2>
  </div>
</section>

<!-- ✅ TRANSACTION TABLE -->
<main class="p-6 fill-blue-700-50 min-h-[40vh]">
  <h2 class="text-xl font-semibold mb-4">📄 Your Transactions</h2>

  {#if loading}
    <p class="text-gray-600 animate-pulse">Loading transactions...</p>
  {:else if error}
    <p class="text-red-600">{error}</p>
  {:else if filteredTransactions.length === 0}
    <p class="text-gray-500">No matching transactions found.</p>
  {:else}
    <div class="overflow-auto rounded-xl shadow-lg border border-gray-200">
      <table class="min-w-full text-sm text-left bg-white">
        <thead class="bg-green-700 text-white">
          <tr>
            <th class="px-4 py-3">Date</th>
            <th class="px-4 py-3">Details</th>
            <th class="px-4 py-3">Amount</th>
            <th class="px-4 py-3">Category</th>
            <th class="px-4 py-3">Status</th> <!-- ✅ NEW -->
          </tr>
        </thead>
        <tbody>
          {#each filteredTransactions as txn (txn.id)}
            <tr class="hover:bg-gray-50 transition">
              <td class="px-4 py-2 border-t">{formatDate(txn.timestamp)}</td>
              <td class="px-4 py-2 border-t">{txn.details}</td>
              <td class="px-4 py-2 border-t font-semibold {txn.amount < 0 ? 'text-red-600' : 'text-green-600'}">
                {txn.amount.toLocaleString()} MWK
              </td>
              <td class="px-4 py-2 border-t">
                <span class="inline-block px-2 py-1 text-xs bg-indigo-100 text-indigo-800 rounded-full">
                  {txn.category}
                </span>
              </td>
              <td class="px-4 py-2 border-t">
                {#if txn.needs_confirmation}
                  <span class="inline-block px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                    ⚠ Needs Confirmation
                  </span>
                {:else}
                  <span class="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                    ✅ Confirmed
                  </span>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</main>
