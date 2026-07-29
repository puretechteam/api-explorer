function FiltersManager() {
this.categoryFilter = document.getElementById('categoryFilter');
this.searchInput = document.getElementById('searchInput');
this.resetBtn = document.getElementById('resetBtn');
this.resultCount = document.getElementById('resultCount');
}

FiltersManager.prototype.init = function() {
this.categoryFilter.addEventListener('change', () => this.applyFilters());
this.searchInput.addEventListener('input', () => this.applyFilters());
this.resetBtn.addEventListener('click', () => this.resetFilters());
};

FiltersManager.prototype.applyFilters = function() {
const searchTerm = this.searchInput.value.toLowerCase().trim();
const category = this.categoryFilter.value;
const cards = document.querySelectorAll('.api-card');
let visibleCount = 0;

cards.forEach(card => {
const name = card.dataset.name || '';
const desc = card.dataset.description || '';
const tags = card.dataset.tags || '';
const cardCategory = card.dataset.category || '';

const matchesSearch = !searchTerm ||
name.includes(searchTerm) ||
desc.includes(searchTerm) ||
tags.includes(searchTerm);
const matchesCategory = !category || cardCategory === category;

if (matchesSearch && matchesCategory) {
card.style.display = '';
visibleCount++;
} else {
card.style.display = 'none';
}
});

this.resultCount.textContent = `${visibleCount} API${visibleCount !== 1 ? 's' : ''} shown`;
};

FiltersManager.prototype.resetFilters = function() {
this.searchInput.value = '';
this.categoryFilter.value = '';
this.applyFilters();
};