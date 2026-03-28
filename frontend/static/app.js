const API_CANDIDATES = [
  `${window.location.origin}/api/v1`,
  `${window.location.protocol}//${window.location.hostname}:8000/api/v1`,
  'http://127.0.0.1:8000/api/v1',
  'http://localhost:8000/api/v1',
].filter((value, index, list) => list.indexOf(value) === index);

const app = document.getElementById('app');
const nairaFormatter = new Intl.NumberFormat('en-NG', {
  style: 'currency',
  currency: 'NGN',
  maximumFractionDigits: 0,
});

const state = {
  products: [],
  filteredProducts: [],
  users: [],
  selectedProduct: null,
  recommendations: [],
  recentInteractions: [],
  loading: false,
  error: '',
  notice: '',
  category: '',
  search: '',
  sort: 'rating',
  userId: '1',
  strategy: 'hybrid',
  autoTrackedViewKey: '',
  workingApiBase: '',
};

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function route() {
  const hash = window.location.hash || '#/';
  const [path] = hash.slice(1).split('?');
  return path || '/';
}

function categories() {
  return [...new Set(state.products.map((product) => product.category).filter(Boolean))].sort();
}

function activeUser() {
  return state.users.find((user) => String(user.id) === String(state.userId)) || null;
}

function clearMessages() {
  state.error = '';
  state.notice = '';
}

function formatRating(product) {
  const rating = Number(product.average_rating || 0).toFixed(1);
  const reviews = Number(product.review_count || 0);
  return `${rating} rating${reviews ? ` - ${reviews} reviews` : ''}`;
}

function formatPrice(product) {
  const price = Number(product.price);
  return Number.isFinite(price) && price > 0
    ? `${nairaFormatter.format(price)} estimated`
    : 'Price unavailable';
}

function productName(productId) {
  const match = state.products.find((product) => Number(product.id) === Number(productId));
  return match?.name || `Product #${productId}`;
}

function strategyDescription() {
  switch (state.strategy) {
    case 'collaborative':
      return 'Uses similar user behavior from the seeded interaction history.';
    case 'content':
      return 'Matches products with similar catalog attributes and descriptions.';
    default:
      return 'Blends user behavior, catalog similarity, and popularity fallback.';
  }
}

function heroStats() {
  const totalProducts = state.products.length;
  const totalCategories = categories().length;
  const reviewedProducts = state.products.filter((product) => Number(product.review_count || 0) > 0).length;
  return { totalProducts, totalCategories, reviewedProducts };
}

function featuredSelections() {
  const featured = [...state.products]
    .sort((left, right) => Number(right.review_count || 0) - Number(left.review_count || 0))
    .slice(0, 4);
  const editorPicks = [...state.products]
    .sort((left, right) => Number(right.average_rating || 0) - Number(left.average_rating || 0))
    .slice(0, 4);
  return { featured, editorPicks };
}

function quickStartSteps() {
  return [
    'Pick a demo user from the top bar',
    'Browse products or open recommendations',
    'Click, add to cart, or purchase to influence results',
  ];
}

function applyFilters() {
  const query = state.search.trim().toLowerCase();
  state.filteredProducts = state.products.filter((product) => {
    const categoryMatch = !state.category || product.category === state.category;
    const textMatch =
      !query ||
      product.name.toLowerCase().includes(query) ||
      String(product.brand || '').toLowerCase().includes(query) ||
      String(product.description || '').toLowerCase().includes(query);
    return categoryMatch && textMatch;
  });

  state.filteredProducts.sort((left, right) => {
    if (state.sort === 'reviews') {
      return Number(right.review_count || 0) - Number(left.review_count || 0);
    }
    if (state.sort === 'name') {
      return String(left.name || '').localeCompare(String(right.name || ''));
    }
    return Number(right.average_rating || 0) - Number(left.average_rating || 0);
  });
}

function backendErrorMessage() {
  return `Could not reach the backend API. Tried: ${API_CANDIDATES.join(', ')}. Make sure the backend window is running, then open /health on port 8000.`;
}

async function apiRequest(path, options = {}) {
  const preferredBases = state.workingApiBase
    ? [state.workingApiBase, ...API_CANDIDATES.filter((base) => base !== state.workingApiBase)]
    : API_CANDIDATES;

  let lastError = null;

  for (const base of preferredBases) {
    try {
      const response = await fetch(`${base}${path}`, options);
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      state.workingApiBase = base;
      return response;
    } catch (error) {
      lastError = error;
    }
  }

  if (lastError instanceof TypeError) {
    throw new Error(backendErrorMessage());
  }

  throw lastError || new Error(backendErrorMessage());
}

async function fetchJson(path) {
  const response = await apiRequest(path, {
    headers: {
      Accept: 'application/json',
    },
  });
  return response.json();
}

async function sendJson(path, method, payload) {
  const response = await apiRequest(path, {
    method,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  return response.json();
}

async function loadProducts() {
  state.loading = true;
  state.error = '';
  render();
  try {
    state.products = await fetchJson('/products/?limit=100');
    applyFilters();
  } catch (error) {
    state.error = error.message;
  } finally {
    state.loading = false;
    render();
  }
}

async function loadUsers() {
  try {
    state.users = await fetchJson('/users/?limit=20');
    if (!activeUser() && state.users.length) {
      state.userId = String(state.users[0].id);
    }
  } catch (error) {
    state.error = error.message;
  }
}

async function loadRecentInteractions() {
  if (!state.userId) {
    state.recentInteractions = [];
    return;
  }
  try {
    state.recentInteractions = await fetchJson(
      `/interactions/user/${encodeURIComponent(state.userId)}?limit=6`,
    );
  } catch (error) {
    state.error = error.message;
  }
}

async function loadProduct(id) {
  state.loading = true;
  state.error = '';
  render();
  try {
    state.selectedProduct = await fetchJson(`/products/${id}`);
  } catch (error) {
    state.error = error.message;
    state.selectedProduct = null;
  } finally {
    state.loading = false;
    render();
  }
}

async function loadRecommendations() {
  state.loading = true;
  clearMessages();
  render();
  try {
    const payload = await fetchJson(
      `/recommendations/user/${encodeURIComponent(state.userId)}?strategy=${encodeURIComponent(state.strategy)}&limit=8`,
    );
    const products = await Promise.all(
      payload.recommendations.map((item) => fetchJson(`/products/${item.product_id}`).catch(() => null)),
    );
    state.recommendations = payload.recommendations.map((item, index) => ({
      ...item,
      product: products[index],
    }));
  } catch (error) {
    state.error = error.message;
    state.recommendations = [];
  } finally {
    state.loading = false;
    render();
  }
}

async function recordInteraction(interactionType, productId, rating = null) {
  if (!state.userId) {
    state.error = 'Select a user first.';
    render();
    return;
  }

  try {
    await sendJson('/interactions/', 'POST', {
      user_id: Number(state.userId),
      product_id: Number(productId),
      interaction_type: interactionType,
      rating,
    });
    state.notice = `Saved ${interactionType.replaceAll('_', ' ')} for ${activeUser()?.first_name || 'selected user'}.`;
    await loadRecentInteractions();
    if (route().startsWith('/recommendations')) {
      await loadRecommendations();
    } else {
      render();
    }
  } catch (error) {
    state.error = error.message;
    render();
  }
}

function productCard(product) {
  const badge = Number(product.average_rating || 0) >= 4.5
    ? '<span class="card-badge">Top rated</span>'
    : Number(product.review_count || 0) >= 1000
      ? '<span class="card-badge subtle">Popular</span>'
      : '';
  const image = product.image_urls?.[0]
    ? `<img class="card-image" src="${escapeHtml(product.image_urls[0])}" alt="${escapeHtml(product.name)}" />`
    : `<div class="card-image"></div>`;
  return `
    <a class="card" href="#/product/${product.id}">
      ${badge}
      ${image}
      <div class="card-body">
        <div class="chip">${escapeHtml(product.category || 'Category')}</div>
        <h4>${escapeHtml(product.name)}</h4>
        <div class="card-price">${escapeHtml(formatPrice(product))}</div>
        <div class="meta">
          <div>${escapeHtml(product.brand || 'Unknown brand')}</div>
          <div>${escapeHtml(formatRating(product))}</div>
        </div>
      </div>
    </a>
  `;
}

function recommendationCard(item) {
  const product = item.product;
  if (!product) {
    return `
      <div class="card">
        <div class="card-body">
          <div class="chip">Product ${item.product_id}</div>
          <h4>Unavailable</h4>
          <div class="meta">
            <div>Score ${Number(item.score || 0).toFixed(2)}</div>
            <div>${escapeHtml(item.reason)}</div>
          </div>
        </div>
      </div>
    `;
  }
  return `
    <a class="card" href="#/product/${product.id}">
      <span class="card-badge accent">Recommended</span>
      ${product.image_urls?.[0] ? `<img class="card-image" src="${escapeHtml(product.image_urls[0])}" alt="${escapeHtml(product.name)}" />` : `<div class="card-image"></div>`}
      <div class="card-body">
        <div class="chip">Score ${Number(item.score || 0).toFixed(2)}</div>
        <h4>${escapeHtml(product.name)}</h4>
        <div class="card-price">${escapeHtml(formatPrice(product))}</div>
        <div class="meta">
          <div>${escapeHtml(product.brand || 'Unknown brand')}</div>
          <div>${escapeHtml(item.reason)}</div>
        </div>
      </div>
    </a>
  `;
}

function homeView() {
  const stats = heroStats();
  const { featured, editorPicks } = featuredSelections();
  const steps = quickStartSteps()
    .map((step, index) => `<li><span>${index + 1}</span>${escapeHtml(step)}</li>`)
    .join('');
  const categoryOptions = categories()
    .map((category) => `<option value="${escapeHtml(category)}"${state.category === category ? ' selected' : ''}>${escapeHtml(category)}</option>`)
    .join('');

  return `
    <section class="hero">
      <article class="hero-card">
        <span class="eyebrow">Live catalog</span>
        <h2>Browse the products we loaded from your new dataset.</h2>
        <p>The frontend is now talking directly to the backend API, so we can explore real catalog data even without the Vite dev server.</p>
        <div class="stats">
          <div class="stat"><strong>${stats.totalProducts}</strong><span>products loaded</span></div>
          <div class="stat"><strong>${stats.totalCategories}</strong><span>categories</span></div>
          <div class="stat"><strong>${stats.reviewedProducts}</strong><span>reviewed items</span></div>
        </div>
        <div class="guide-list">
          ${steps}
        </div>
      </article>
      <aside class="side-card">
        <h3>What you can do here</h3>
        <p>Filter the catalog, compare products, and jump into recommendation testing with your seeded users.</p>
        <div class="side-card-stack">
          <div class="runtime-badge">Running in fallback mode</div>
          ${
            activeUser()
              ? `<div class="side-user">
                  <strong>${escapeHtml(activeUser().first_name || activeUser().username)}</strong>
                  <span class="muted">Current test user</span>
                </div>`
              : ''
          }
          <div class="side-user">
            <strong>Estimated prices in Naira</strong>
            <span class="muted">Prices are demo-ready estimates based on product type, brand, pack size, and category.</span>
          </div>
          <button class="button secondary" data-route="#/recommendations">Open recommendations</button>
        </div>
      </aside>
    </section>

    <section class="layout">
      <aside class="panel">
        <div class="section-title">
          <h3>Refine</h3>
        </div>
        <div class="filter-stack">
          <input id="searchInput" type="text" placeholder="Search by name, brand, description" value="${escapeHtml(state.search)}" />
          <select id="categorySelect">
            <option value="">All categories</option>
            ${categoryOptions}
          </select>
          <select id="sortSelect">
            <option value="rating"${state.sort === 'rating' ? ' selected' : ''}>Sort by rating</option>
            <option value="reviews"${state.sort === 'reviews' ? ' selected' : ''}>Sort by reviews</option>
            <option value="name"${state.sort === 'name' ? ' selected' : ''}>Sort by name</option>
          </select>
        </div>
      </aside>

      <section class="panel">
        <div class="section-title">
          <h3>Products</h3>
          <span class="muted">${state.filteredProducts.length} showing</span>
        </div>
        ${
          state.loading
            ? '<div class="empty">Loading products...</div>'
            : state.filteredProducts.length
              ? `<div class="grid">${state.filteredProducts.map(productCard).join('')}</div>`
              : '<div class="empty">No products matched this filter.</div>'
        }
      </section>
    </section>

    <section class="showcase-grid">
      <section class="panel">
        <div class="section-title">
          <h3>Most reviewed</h3>
          <span class="muted">High-confidence products</span>
        </div>
        <div class="mini-grid">
          ${featured.map(productCard).join('')}
        </div>
      </section>
      <section class="panel">
        <div class="section-title">
          <h3>Editor’s picks</h3>
          <span class="muted">Highest-rated catalog picks</span>
        </div>
        <div class="mini-grid">
          ${editorPicks.map(productCard).join('')}
        </div>
      </section>
    </section>
  `;
}

function productView() {
  if (state.loading) {
    return '<section class="panel"><div class="empty">Loading product...</div></section>';
  }
  if (!state.selectedProduct) {
    return '<section class="panel"><div class="empty">Product not found.</div></section>';
  }

  const product = state.selectedProduct;
  const tags = (product.tags || []).slice(0, 14).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join('');
  const user = activeUser();
  return `
    <section class="panel">
      <div class="detail">
        <div>
          ${
            product.image_urls?.[0]
              ? `<img class="detail-image" src="${escapeHtml(product.image_urls[0])}" alt="${escapeHtml(product.name)}" />`
              : '<div class="detail-image"></div>'
          }
        </div>
        <div class="detail-copy">
          <div class="chip">${escapeHtml(product.category || 'Category')}</div>
          <h2>${escapeHtml(product.name)}</h2>
          <div class="detail-highlights">
            <span class="card-badge accent">Portfolio demo product</span>
            ${Number(product.average_rating || 0) >= 4.5 ? '<span class="card-badge">Highly rated</span>' : ''}
          </div>
          <div class="meta">
            <div>${escapeHtml(product.brand || 'Unknown brand')}</div>
            <div>${escapeHtml(formatRating(product))}</div>
            <div>${escapeHtml(formatPrice(product))}</div>
          </div>
          <div class="summary">
            <p>${escapeHtml(product.description || 'No description available for this product yet.')}</p>
          </div>
          ${tags ? `<div class="tags">${tags}</div>` : ''}
          <div class="interaction-bar">
            <div class="muted">Tracking actions as ${escapeHtml(user?.first_name || user?.username || 'user')}</div>
            <div class="interaction-actions">
              <button class="button secondary" data-interaction="click" data-product-id="${product.id}">Click</button>
              <button class="button secondary" data-interaction="add_to_cart" data-product-id="${product.id}">Add to cart</button>
              <button class="button" data-interaction="purchase" data-product-id="${product.id}" data-rating="${Math.max(4, Number(product.average_rating || 4))}">Purchase</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}

function recommendationsView() {
  const user = activeUser();
  const userOptions = state.users
    .map(
      (candidate) =>
        `<option value="${escapeHtml(candidate.id)}"${String(candidate.id) === String(state.userId) ? ' selected' : ''}>${escapeHtml(candidate.first_name || candidate.username)} (#${escapeHtml(candidate.id)})</option>`,
    )
    .join('');

  return `
    <section class="layout">
      <aside class="panel">
        <div class="section-title">
          <h3>Recommendation test</h3>
        </div>
        <div class="recommend-form">
          <select id="userSelect">
            ${userOptions}
          </select>
          <select id="strategySelect">
            <option value="hybrid"${state.strategy === 'hybrid' ? ' selected' : ''}>Hybrid</option>
            <option value="collaborative"${state.strategy === 'collaborative' ? ' selected' : ''}>Collaborative</option>
            <option value="content"${state.strategy === 'content' ? ' selected' : ''}>Content</option>
          </select>
          <button class="button" id="recommendButton">Fetch recommendations</button>
        </div>
        <p class="muted">${escapeHtml(strategyDescription())}</p>
        ${
          user
            ? `<div class="user-summary">
                <strong>${escapeHtml(user.first_name || user.username)} ${escapeHtml(user.last_name || '')}</strong>
                <span>${escapeHtml(user.email)}</span>
                <span class="muted">Seeded profile for testing recommendation quality and user journeys.</span>
              </div>`
            : '<p class="muted">Loading seeded users...</p>'
        }
        ${
          state.recentInteractions.length
            ? `<div class="history-list">
                ${state.recentInteractions
                  .slice(0, 4)
                  .map(
                    (interaction) =>
                      `<div class="history-item">
                        <strong>${escapeHtml(interaction.interaction_type.replaceAll('_', ' '))}</strong>
                        <span class="muted">${escapeHtml(productName(interaction.product_id))}</span>
                      </div>`,
                  )
                  .join('')}
              </div>`
            : ''
        }
      </aside>

      <section class="panel">
        <div class="section-title">
          <h3>Results</h3>
          <span class="muted">${state.recommendations.length} items</span>
        </div>
        ${
          state.recommendations[0]?.product
            ? `<div class="result-spotlight">
                <span class="eyebrow">Top match</span>
                <h4>${escapeHtml(state.recommendations[0].product.name)}</h4>
                <p>${escapeHtml(state.recommendations[0].reason)}</p>
                <div class="spotlight-actions">
                  <a class="button secondary" href="#/product/${state.recommendations[0].product.id}">View product</a>
                </div>
              </div>`
            : ''
        }
        ${
          state.loading
            ? '<div class="empty">Loading recommendations...</div>'
            : state.recommendations.length
              ? `<div class="grid">${state.recommendations.map(recommendationCard).join('')}</div>`
              : '<div class="empty">Choose a user and strategy, then fetch recommendations to see personalized results.</div>'
        }
      </section>
    </section>
  `;
}

function render() {
  const currentRoute = route();
  const isHome = currentRoute === '/';
  const isRecommendations = currentRoute.startsWith('/recommendations');
  const topUserOptions = state.users
    .map(
      (candidate) =>
        `<option value="${escapeHtml(candidate.id)}"${String(candidate.id) === String(state.userId) ? ' selected' : ''}>${escapeHtml(candidate.first_name || candidate.username)}</option>`,
    )
    .join('');

  let pageHtml = homeView();
  if (currentRoute.startsWith('/product/')) {
    pageHtml = productView();
  } else if (isRecommendations) {
    pageHtml = recommendationsView();
  }

  app.innerHTML = `
    <div class="shell">
      <header class="topbar">
        <div class="brand">
          <h1>RecommendHub</h1>
          <p>Dataset-driven storefront and recommendation tester</p>
        </div>
        <div class="runtime-badge">Static fallback active</div>
        ${
          state.users.length
            ? `<label class="top-user-picker">
                <span>Demo user</span>
                <select id="topUserSelect">${topUserOptions}</select>
              </label>`
            : `<div class="current-user-badge">No user selected</div>`
        }
        <nav class="nav">
          <a href="#/" class="${isHome ? 'active' : ''}">Catalog</a>
          <a href="#/recommendations" class="${isRecommendations ? 'active' : ''}">Recommendations</a>
        </nav>
      </header>
      ${state.error ? `<div class="error" style="margin-top:18px;">${escapeHtml(state.error)}</div>` : ''}
      ${state.notice ? `<div class="notice" style="margin-top:18px;">${escapeHtml(state.notice)}</div>` : ''}
      ${pageHtml}
      <div class="footer">Frontend fallback server is running without Vite so we can keep shipping.</div>
    </div>
  `;

  bindEvents();
}

function bindEvents() {
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (event) => {
      state.search = event.target.value;
      applyFilters();
      render();
    });
  }

  const categorySelect = document.getElementById('categorySelect');
  if (categorySelect) {
    categorySelect.addEventListener('change', (event) => {
      state.category = event.target.value;
      applyFilters();
      render();
    });
  }

  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', (event) => {
      state.sort = event.target.value || 'rating';
      applyFilters();
      render();
    });
  }

  const routeButton = document.querySelector('[data-route]');
  if (routeButton) {
    routeButton.addEventListener('click', () => {
      window.location.hash = routeButton.getAttribute('data-route');
    });
  }

  const userSelect = document.getElementById('userSelect');
  if (userSelect) {
    userSelect.addEventListener('change', (event) => {
      state.userId = event.target.value || '1';
      state.autoTrackedViewKey = '';
      clearMessages();
      loadRecentInteractions().then(() => render());
    });
  }

  const topUserSelect = document.getElementById('topUserSelect');
  if (topUserSelect) {
    topUserSelect.addEventListener('change', (event) => {
      state.userId = event.target.value || '1';
      state.autoTrackedViewKey = '';
      clearMessages();
      loadRecentInteractions().then(() => render());
    });
  }

  const strategySelect = document.getElementById('strategySelect');
  if (strategySelect) {
    strategySelect.addEventListener('change', (event) => {
      state.strategy = event.target.value;
      render();
    });
  }

  const recommendButton = document.getElementById('recommendButton');
  if (recommendButton) {
    recommendButton.addEventListener('click', () => {
      loadRecommendations();
    });
  }

  document.querySelectorAll('[data-interaction]').forEach((button) => {
    button.addEventListener('click', (event) => {
      const target = event.currentTarget;
      const interactionType = target.getAttribute('data-interaction');
      const productId = target.getAttribute('data-product-id');
      const ratingRaw = target.getAttribute('data-rating');
      const rating = ratingRaw ? Number(ratingRaw) : null;
      if (interactionType && productId) {
        recordInteraction(interactionType, productId, rating);
      }
    });
  });
}

async function syncRoute() {
  const currentRoute = route();
  if (!state.products.length) {
    await Promise.all([loadProducts(), loadUsers(), loadRecentInteractions()]);
    return;
  }
  if (currentRoute.startsWith('/product/')) {
    const id = currentRoute.split('/')[2];
    if (id) {
      await loadProduct(id);
      const autoKey = `${state.userId}:${id}`;
      if (state.selectedProduct && state.autoTrackedViewKey !== autoKey) {
        state.autoTrackedViewKey = autoKey;
        await recordInteraction('view', id);
        return;
      }
    }
  } else if (currentRoute.startsWith('/recommendations')) {
    await loadRecentInteractions();
    render();
  } else {
    render();
  }
}

window.addEventListener('hashchange', () => {
  state.error = '';
  if (!route().startsWith('/product/')) {
    state.selectedProduct = null;
  }
  syncRoute();
});

Promise.all([loadProducts(), loadUsers(), loadRecentInteractions()]);
