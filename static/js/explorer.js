let allApis = [];
let currentApi = null;
let dataIsStale = false;

const CATEGORY_ICONS = {
finance: '💰',
social: '👥',
weather: '🌦',
maps: '🗺',
email: '📧',
storage: '💾',
ai: '🤖',
music: '🎵',
video: '🎬',
news: '📰',
sports: '⚽',
health: '🏥',
crypto: '₿',
ecommerce: '🛒',
developer: '💻'
};

function getCategoryIcon(category) {
return CATEGORY_ICONS[category] || '📄';
}

async function loadData() {
try {
const response = await fetch('/api/data');
if (!response.ok) throw new Error('Network response was not ok');
const data = await response.json();
allApis = data;
window.allApis = allApis;
dataIsStale = false;
updateStaleIndicator();
renderDiscover();
renderApis(allApis);
} catch (err) {
console.error('Failed to load API data from server:', err);
showStaleIndicator();
loadBundledData();
}
}

function loadBundledData() {
try {
const response = fetch('/static/data/apis.json');
response.then(res => {
if (!res.ok) throw new Error('Bundled data unavailable');
return res.json();
}).then(data => {
allApis = data;
window.allApis = allApis;
dataIsStale = true;
updateStaleIndicator();
renderDiscover();
renderApis(allApis);
}).catch(err => {
console.error('Failed to load bundled data:', err);
document.getElementById('apiGrid').innerHTML = '<p>Unable to load API data. Please check your connection and try again.</p>';
});
} catch (err) {
console.error('Failed to load bundled data:', err);
document.getElementById('apiGrid').innerHTML = '<p>Unable to load API data.</p>';
}
}

function updateStaleIndicator() {
const indicator = document.getElementById('staleIndicator');
if (dataIsStale) {
indicator.classList.add('visible');
} else {
indicator.classList.remove('visible');
}
}

function showStaleIndicator() {
dataIsStale = true;
updateStaleIndicator();
}

async function loadCategories() {
try {
const response = await fetch('/api/categories');
const categories = await response.json();
const select = document.getElementById('categoryFilter');
categories.forEach(cat => {
const opt = document.createElement('option');
opt.value = cat;
opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
select.appendChild(opt);
});
} catch (err) {
console.error('Failed to load categories:', err);
}
}

const CATEGORY_COLORS = {
finance: '#10b981',
social: '#8b5cf6',
weather: '#06b6d4',
maps: '#f59e0b',
email: '#3b82f6',
storage: '#6366f1',
ai: '#ec4899',
music: '#8b5cf6',
video: '#ef4444',
news: '#f97316',
sports: '#22c55e',
health: '#14b8a6',
crypto: '#f59e0b',
ecommerce: '#6366f1',
developer: '#0ea5e9'
};

function getCategoryColor(category) {
return CATEGORY_COLORS[category] || '#6b7280';
}

function renderPopular() {
const section = document.getElementById('popularSection');
if (!section) return;
const sorted = [...allApis].sort((a, b) => (b.endpoints || []).length - (a.endpoints || []).length).slice(0, 5);
const container = document.getElementById('popularList');
if (!container) return;
container.innerHTML = '';
sorted.forEach(api => {
const card = document.createElement('div');
card.className = 'popular-card';
const icon = getCategoryIcon(api.category);
const color = getCategoryColor(api.category);
card.innerHTML = `
<span class="popular-icon" style="color:${color}">${icon}</span>
<span class="popular-name">${escapeHtml(api.name)}</span>
<span class="popular-eps">${(api.endpoints || []).length} endpoints</span>
`;
card.addEventListener('click', () => {
openDetail(api);
});
container.appendChild(card);
});
}

function renderDiscover() {
const grid = document.getElementById('discoverGrid');
if (!grid) return;
const categories = {};
allApis.forEach(api => {
const cat = api.category || 'other';
if (!categories[cat]) categories[cat] = { count: 0, icon: getCategoryIcon(cat), color: getCategoryColor(cat) };
categories[cat].count++;
});
grid.innerHTML = '';
Object.entries(categories).forEach(([cat, info]) => {
const card = document.createElement('div');
card.className = 'discover-card';
card.style.borderTopColor = info.color;
card.innerHTML = `
<span class="discover-icon" style="color:${info.color}">${info.icon}</span>
<span class="discover-name">${cat.charAt(0).toUpperCase() + cat.slice(1)}</span>
<span class="discover-count">${info.count} API${info.count !== 1 ? 's' : ''}</span>
`;
card.addEventListener('click', () => {
document.getElementById('categoryFilter').value = cat;
renderApis(getFilteredApis());
});
grid.appendChild(card);
});
}

function renderApis(apis) {
const grid = document.getElementById('apiGrid');
const noResults = document.getElementById('noResults');
const resultCount = document.getElementById('resultCount');

grid.innerHTML = '';
resultCount.textContent = `${apis.length} API${apis.length !== 1 ? 's' : ''} found`;

if (apis.length === 0) {
noResults.style.display = 'block';
return;
}

noResults.style.display = 'none';

apis.forEach(api => {
const card = document.createElement('div');
card.className = 'api-card';
card.dataset.name = api.name.toLowerCase();
card.dataset.category = api.category;
card.dataset.tags = (api.tags || []).join(' ').toLowerCase();
card.dataset.description = (api.description || '').toLowerCase();

const isFav = FavoritesManager.isFavorite(api.name);
const icon = getCategoryIcon(api.category);

card.innerHTML = `
<div class="card-header">
<span class="card-icon">${icon}</span>
<h3>${escapeHtml(api.name)}</h3>
<button class="star-btn ${isFav ? 'active' : ''}" data-api="${escapeHtml(api.name)}" aria-label="Toggle favorite">&#9733;</button>
</div>
<span class="card-category">${escapeHtml(api.category)}</span>
<p class="card-desc">${escapeHtml(api.description)}</p>
<div class="card-tags">
${(api.tags || []).slice(0, 5).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
</div>
`;

card.addEventListener('click', (e) => {
if (e.target.closest('.star-btn')) return;
openDetail(api);
});

card.querySelector('.star-btn').addEventListener('click', (e) => {
e.stopPropagation();
const apiName = e.target.dataset.api;
const apiObj = allApis.find(a => a.name === apiName);
if (apiObj) {
FavoritesManager.toggle(apiObj);
e.target.classList.toggle('active');
renderApis(getFilteredApis());
}
});

grid.appendChild(card);
});
}

function getFilteredApis() {
const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
const category = document.getElementById('categoryFilter').value;

return allApis.filter(api => {
const matchesSearch = !searchTerm ||
api.name.toLowerCase().includes(searchTerm) ||
api.description.toLowerCase().includes(searchTerm) ||
(api.tags || []).some(t => t.toLowerCase().includes(searchTerm));
const matchesCategory = !category || api.category === category;
return matchesSearch && matchesCategory;
});
}

function openDetail(api) {
currentApi = api;
const panel = document.getElementById('detailPanel');
document.getElementById('detailName').textContent = api.name;
document.getElementById('detailCategory').textContent = api.category;
document.getElementById('detailDescription').textContent = api.description;
document.getElementById('detailAuth').textContent = api.auth;
document.getElementById('detailRateLimit').textContent = api.rate_limit;
document.getElementById('detailDocs').href = api.docs_url;

const endpointsList = document.getElementById('detailEndpoints');
endpointsList.innerHTML = '';
(api.endpoints || []).forEach(ep => {
const li = document.createElement('li');
li.textContent = ep;
endpointsList.appendChild(li);
});

const tagsContainer = document.getElementById('detailTags');
tagsContainer.innerHTML = '';
(api.tags || []).forEach(tag => {
const span = document.createElement('span');
span.textContent = tag;
tagsContainer.appendChild(span);
});

const curl = `curl -X GET "${api.docs_url}" \\
  -H "Authorization: Bearer YOUR_API_KEY"`;
document.getElementById('curlSnippet').textContent = curl;

const favBtn = document.getElementById('toggleFavorite');
const isFav = FavoritesManager.isFavorite(api.name);
favBtn.textContent = isFav ? 'Remove from Favorites' : 'Add to Favorites';
favBtn.classList.toggle('favorited', isFav);

panel.style.display = 'block';
document.getElementById('overlay').classList.add('active');

RecentlyViewedManager.add(api);
}

function closeDetail() {
document.getElementById('detailPanel').style.display = 'none';
document.getElementById('overlay').classList.remove('active');
currentApi = null;
}

function escapeHtml(str) {
const div = document.createElement('div');
div.textContent = str;
return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
loadData();
loadCategories();

document.getElementById('searchBtn').addEventListener('click', () => {
renderApis(getFilteredApis());
});

document.getElementById('searchInput').addEventListener('input', () => {
renderApis(getFilteredApis());
});

document.getElementById('categoryFilter').addEventListener('change', () => {
renderApis(getFilteredApis());
});

document.getElementById('resetBtn').addEventListener('click', () => {
document.getElementById('searchInput').value = '';
document.getElementById('categoryFilter').value = '';
renderApis(getFilteredApis());
});

document.getElementById('closeDetail').addEventListener('click', closeDetail);

document.getElementById('overlay').addEventListener('click', closeDetail);

document.getElementById('copyCurl').addEventListener('click', () => {
const text = document.getElementById('curlSnippet').textContent;
navigator.clipboard.writeText(text).then(() => {
const btn = document.getElementById('copyCurl');
btn.textContent = 'Copied!';
setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
});
});

document.getElementById('toggleFavorite').addEventListener('click', () => {
if (currentApi) {
FavoritesManager.toggle(currentApi);
const isFav = FavoritesManager.isFavorite(currentApi.name);
const btn = document.getElementById('toggleFavorite');
btn.textContent = isFav ? 'Remove from Favorites' : 'Add to Favorites';
btn.classList.toggle('favorited', isFav);
renderApis(getFilteredApis());
}
});

document.getElementById('dismissStale').addEventListener('click', () => {
dataIsStale = false;
updateStaleIndicator();
});

RecentlyViewedManager.render();
FavoritesManager.renderSidebar();
renderDiscover();
renderPopular();
});