const FavoritesManager = {
STORAGE_KEY: 'api_explorer_favorites',

getFavorites: function() {
try {
const data = localStorage.getItem(this.STORAGE_KEY);
return data ? JSON.parse(data) : [];
} catch (e) {
return [];
}
},

saveFavorites: function(favorites) {
try {
localStorage.setItem(this.STORAGE_KEY, JSON.stringify(favorites));
} catch (e) {
console.warn('Failed to save favorites to localStorage:', e);
}
},

isFavorite: function(apiName) {
return this.getFavorites().some(f => f.name === apiName);
},

toggle: function(api) {
let favorites = this.getFavorites();
const index = favorites.findIndex(f => f.name === api.name);
if (index > -1) {
favorites.splice(index, 1);
} else {
favorites.push({
name: api.name,
category: api.category,
description: api.description,
auth: api.auth,
rate_limit: api.rate_limit,
endpoints: api.endpoints,
docs_url: api.docs_url,
tags: api.tags
});
}
this.saveFavorites(favorites);
this.renderSidebar();
},

remove: function(apiName) {
let favorites = this.getFavorites().filter(f => f.name !== apiName);
this.saveFavorites(favorites);
this.renderSidebar();
},

renderSidebar: function() {
const container = document.getElementById('favoritesList');
const noFavorites = document.getElementById('noFavorites');
const favorites = this.getFavorites();

container.innerHTML = '';

if (favorites.length === 0) {
noFavorites.style.display = 'block';
return;
}

noFavorites.style.display = 'none';

favorites.forEach(fav => {
const chip = document.createElement('span');
chip.className = 'favorite-chip';
chip.innerHTML = `${escapeHtml(fav.name)} <span class="remove-fav" data-name="${escapeHtml(fav.name)}">&times;</span>`;
chip.addEventListener('click', (e) => {
if (e.target.classList.contains('remove-fav')) {
FavoritesManager.remove(fav.name);
return;
}
const apiObj = window.allApis ? window.allApis.find(a => a.name === fav.name) : null;
if (apiObj) {
openDetail(apiObj);
}
});
container.appendChild(chip);
});
}
};

const RecentlyViewedManager = {
STORAGE_KEY: 'api_explorer_recent',
MAX_ITEMS: 10,

getRecent: function() {
try {
const data = localStorage.getItem(this.STORAGE_KEY);
return data ? JSON.parse(data) : [];
} catch (e) {
return [];
}
},

saveRecent: function(recent) {
try {
localStorage.setItem(this.STORAGE_KEY, JSON.stringify(recent));
} catch (e) {
console.warn('Failed to save recent to localStorage:', e);
}
},

add: function(api) {
let recent = this.getRecent();
recent = recent.filter(r => r.name !== api.name);
recent.unshift({
name: api.name,
category: api.category,
description: api.description,
auth: api.auth,
rate_limit: api.rate_limit,
endpoints: api.endpoints,
docs_url: api.docs_url,
tags: api.tags
});
if (recent.length > this.MAX_ITEMS) {
recent = recent.slice(0, this.MAX_ITEMS);
}
this.saveRecent(recent);
this.render();
},

render: function() {
const container = document.getElementById('recentlyViewedList');
const noRecent = document.getElementById('noRecent');
const recent = this.getRecent();

container.innerHTML = '';

if (recent.length === 0) {
noRecent.style.display = 'block';
return;
}

noRecent.style.display = 'none';

recent.forEach(api => {
const chip = document.createElement('span');
chip.className = 'recently-viewed-chip';
chip.textContent = api.name;
chip.addEventListener('click', () => {
const apiObj = window.allApis ? window.allApis.find(a => a.name === api.name) : null;
if (apiObj) {
openDetail(apiObj);
}
});
container.appendChild(chip);
});
}
};

function escapeHtml(str) {
const div = document.createElement('div');
div.textContent = str;
return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
FavoritesManager.renderSidebar();
});