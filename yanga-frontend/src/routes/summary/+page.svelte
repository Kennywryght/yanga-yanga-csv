<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import { BACKEND_URL } from '$lib/config';
  import Chart from 'chart.js/auto';
  import jsPDF from 'jspdf';
  import 'jspdf-autotable';

  interface BreakdownItem {
    Category: string;
    'Amount (MWK)': number;
    Percentage: number;
  }

  interface Summary {
    file_id: string;
    total_income: number;
    total_spent: number;
    category_breakdown: BreakdownItem[];
    top_3_categories: string[];
    monthly_trends: Record<string, number>;
  }

  let fileId = '';
  $: fileId = get(page).url.searchParams.get('file_id') || '';

  let summary: Summary | null = null;
  let loading = true;
  let error: string | null = null;
  let doughnutChart: Chart | null = null;
  let barChart: Chart | null = null;
  let lineChart: Chart | null = null;

  let startDate = '';
  let endDate = '';

  const categoryColors: Record<string, string> = {
    Food: '#f97316', Transport: '#3b82f6', Bundles: '#a855f7', Betting: '#ef4444',
    Utilities: '#eab308', Other: '#10b981', Entertainment: '#14b8a6', Uncategorized: '#9ca3af'
  };

  onMount(async () => {
    if (!fileId) {
      error = 'Missing file ID. Please go back and upload your transaction file first.';
      loading = false;
      return;
    }

    try {
      const res = await fetch(`${BACKEND_URL}/dashboard/${fileId}`);
      if (!res.ok) throw new Error('Failed to fetch summary. Please go back and re-upload your transactions.');
      summary = await res.json();
      setTimeout(drawCharts, 100);
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  });

  onDestroy(() => {
    doughnutChart?.destroy();
    barChart?.destroy();
    lineChart?.destroy();
  });

  function drawCharts() {
    if (!summary) return;

    const labels = summary.category_breakdown.map(c => c.Category);
    const values = summary.category_breakdown.map(c => c['Amount (MWK)']);
    const colors = labels.map(label => categoryColors[label] || '#9ca3af');

    const doughnutCtx = document.getElementById('doughnutChart') as HTMLCanvasElement;
    const barCtx = document.getElementById('barChart') as HTMLCanvasElement;
    const lineCtx = document.getElementById('lineChart') as HTMLCanvasElement;

    doughnutChart = new Chart(doughnutCtx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          label: 'Spending by Category',
          data: values,
          backgroundColor: colors
        }]
      },
      options: {
        cutout: '50%',
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.label}: MWK ${ctx.parsed.toLocaleString()}`
            }
          }
        }
      }
    });

    barChart = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Amount (MWK)',
          data: values,
          backgroundColor: colors
        }]
      },
      options: {
        scales: {
          y: { beginAtZero: true },
          x: { ticks: { color: '#333' } }
        },
        plugins: { legend: { display: false } }
      }
    });

    const trendLabels = Object.keys(summary.monthly_trends);
    const trendValues = Object.values(summary.monthly_trends);

    lineChart = new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: trendLabels,
        datasets: [{
          label: 'Monthly Spending',
          data: trendValues,
          borderColor: '#2563eb',
          backgroundColor: '#93c5fd',
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        plugins: { legend: { position: 'top' } }
      }
    });
  }

  function exportPDF() {
    if (!summary) return;
    const doc = new jsPDF();
    doc.text('Yanga Yanga Transaction Summary', 14, 20);
    const columns = ['Category', 'Amount (MWK)', 'Percentage'];
    const rows = summary.category_breakdown.map(c => [
      c.Category,
      c['Amount (MWK)'].toLocaleString(),
      `${c.Percentage}%`
    ]);
    // @ts-ignore
    doc.autoTable({ head: [columns], body: rows, startY: 30 });
    const endY = (doc as any).lastAutoTable.finalY || 60;
    doc.text(`Total Income: MWK ${summary.total_income.toLocaleString()}`, 14, endY + 10);
    doc.text(`Total Spent: MWK ${summary.total_spent.toLocaleString()}`, 14, endY + 20);
    doc.save('yanga_summary.pdf');
  }

  function shareViaWhatsApp() {
    if (!summary) return;
    const message = `📊 Yanga Yanga Summary:\n💵 Total Income: MWK ${summary.total_income}\n💸 Total Spent: MWK ${summary.total_spent}\n🧾 Top Categories:\n${summary.category_breakdown.map(c => `- ${c.Category}: MWK ${c['Amount (MWK)']} (${c.Percentage}%)`).join('\n')}`;
    const url = `https://wa.me/?text=${encodeURIComponent(message)}`;
    window.open(url, '_blank');
  }

  function shareViaEmail() {
    if (!summary) return;
    const subject = 'Yanga Yanga Transaction Summary';
    const body = `Here is my spending summary:\n\nTotal Income: MWK ${summary.total_income}\nTotal Spent: MWK ${summary.total_spent}\n\nCategory Breakdown:\n${summary.category_breakdown.map(c => `- ${c.Category}: MWK ${c['Amount (MWK)']} (${c.Percentage}%)`).join('\n')}`;
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  }

  function isTopCategory(cat: string): boolean {
    return summary?.top_3_categories?.includes(cat) ?? false;
  }

  function goBack() {
    window.location.href = '/'; // or '/upload' if that's your upload route
  }
</script>

<style>
  main {
    max-width: 920px;
    margin: 2rem auto;
    background: #f8fafc;
    padding: 2rem;
    border-radius: 1rem;
    color: #1e293b;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
  }

  canvas {
    max-width: 380px;
    margin: 1.5rem auto;
    display: block;
  }

  h1, h2 {
    text-align: center;
    color: #14532d;
    margin-bottom: 1rem;
  }

  .stats {
    margin: 1rem 0;
    text-align: center;
  }

  .stats p {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0.5rem 0;
  }

  ul {
    list-style: none;
    padding: 0;
    margin-top: 1rem;
  }

  li {
    margin-bottom: 0.6rem;
    color: #334155;
    font-weight: 500;
  }

  li.highlight {
    color: #dc2626;
    font-weight: bold;
  }

  .actions {
    margin-top: 2rem;
    text-align: center;
  }

  .actions button {
    background: #15803d;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 0.4rem;
    padding: 0.5rem 1.2rem;
    margin: 0.5rem;
    cursor: pointer;
  }

  .actions button:hover {
    background: #166534;
  }

  .filter-box {
    text-align: center;
    margin-top: 1.5rem;
  }

  .filter-box input {
    padding: 0.4rem;
    border: 1px solid #d1d5db;
    border-radius: 0.4rem;
    margin: 0 0.5rem;
  }

  .error, .loading {
    text-align: center;
    font-weight: bold;
    margin-top: 3rem;
    font-size: 1.1rem;
  }

  .error { color: #b91c1c; }
  .loading { color: #0f5132; }

  .go-back {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
  }

  .go-back button {
    background: #ef4444;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.4rem;
    font-weight: bold;
    border: none;
    cursor: pointer;
  }

  .go-back button:hover {
    background: #b91c1c;
  }
</style>

<main>
  <h1>Summary Dashboard</h1>

  {#if loading}
    <p class="loading">Loading summary...</p>
  {:else if error}
    <p class="error">⚠️ {error}</p>
    <div class="go-back">
      <button on:click={goBack}>⬅️ Go back to Upload</button>
    </div>
  {:else if summary}
    <div class="stats">
      <p>💵 <strong>Total Income:</strong> MWK {summary.total_income.toLocaleString()}</p>
      <p>💸 <strong>Total Spent:</strong> MWK {summary.total_spent.toLocaleString()}</p>
    </div>

    <canvas id="doughnutChart"></canvas>
    <canvas id="barChart"></canvas>
    <canvas id="lineChart"></canvas>

    <div class="filter-box">
      <label>📅 Filter:
        <input type="date" bind:value={startDate} />
        to
        <input type="date" bind:value={endDate} />
      </label>
    </div>

    <div class="stats">
      <h2>Category Breakdown</h2>
      <ul>
        {#each summary.category_breakdown as item}
          <li class={isTopCategory(item.Category) ? 'highlight' : ''}>
            {isTopCategory(item.Category) ? '🌟' : ''} <strong>{item.Category}:</strong> MWK {item["Amount (MWK)"].toLocaleString()} ({item.Percentage}%)
          </li>
        {/each}
      </ul>
    </div>

    <div class="actions">
      <button on:click={exportPDF}>📥 Download PDF</button>
      <button on:click={shareViaWhatsApp}>📲 Share on WhatsApp</button>
      <button on:click={shareViaEmail}>📧 Share via Email</button>
    </div>
  {/if}
</main>
