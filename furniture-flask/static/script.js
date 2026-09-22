function fmt(n){ return "Rs " + Number(n).toLocaleString("en-PK"); }

function showToast(msg){
  const t = document.getElementById('toast');
  if(!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(()=>t.classList.remove('show'), 1800);
}

/* ---------------- Cart drawer open/close ---------------- */
const drawer = document.getElementById('drawer');
const overlay = document.getElementById('overlay');
const cartBtn = document.getElementById('cartBtn');
const drawerClose = document.getElementById('drawerClose');

function openCart(){
  refreshCart();
  drawer.classList.add('open');
  overlay.classList.add('open');
}
function closeCart(){
  drawer.classList.remove('open');
  overlay.classList.remove('open');
}
if(cartBtn) cartBtn.addEventListener('click', openCart);
if(drawerClose) drawerClose.addEventListener('click', closeCart);
if(overlay) overlay.addEventListener('click', closeCart);

/* ---------------- Cart API helpers ---------------- */
async function refreshCart(){
  const res = await fetch('/api/cart');
  const data = await res.json();
  renderDrawer(data);
  updateCartCount(data.count);
}

function updateCartCount(count){
  const el = document.getElementById('cartCount');
  if(el) el.textContent = count;
}

function renderDrawer(data){
  const wrap = document.getElementById('drawerItems');
  if(!data.items.length){
    wrap.innerHTML = `<div class="drawer-empty">Your cart is empty.<br>Start adding something beautiful.</div>`;
  } else {
    wrap.innerHTML = data.items.map(item => `
      <div class="d-item">
        <img src="${item.img}" alt="${item.name}">
        <div class="d-item-info">
          <div class="name">${item.name}</div>
          <div class="meta"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${item.color};margin-right:6px;"></span>Qty ${item.qty}</div>
          <div class="qty-ctrl">
            <button onclick="changeQty('${item.key}',-1)">−</button>
            <span>${item.qty}</span>
            <button onclick="changeQty('${item.key}',1)">+</button>
            <button class="d-remove" onclick="removeItem('${item.key}')">Remove</button>
          </div>
        </div>
        <div class="d-item-price">${fmt(item.line_total)}</div>
      </div>
    `).join('');
  }
  document.getElementById('drawerTotal').textContent = fmt(data.total);
}

async function addToCart(id, color){
  const res = await fetch('/api/cart/add', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({id, color})
  });
  const data = await res.json();
  updateCartCount(data.count);
  showToast("Added to cart");
}

async function changeQty(key, delta){
  const res = await fetch('/api/cart/update', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({key, delta})
  });
  const data = await res.json();
  updateCartCount(data.count);
  refreshCart();
}

async function removeItem(key){
  const res = await fetch('/api/cart/remove', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({key})
  });
  const data = await res.json();
  updateCartCount(data.count);
  refreshCart();
}

const checkoutBtn = document.getElementById('checkoutBtn');
if(checkoutBtn){
  checkoutBtn.addEventListener('click', async () => {
    const res = await fetch('/api/checkout', { method:'POST' });
    if(res.status === 401){
      showToast("Please log in to checkout");
      setTimeout(()=>{ window.location.href = window.LOGIN_URL; }, 900);
      return;
    }
    const data = await res.json();
    if(data.error === 'empty_cart'){
      showToast("Your cart is empty");
      return;
    }
    if(data.ok){
      showToast("Order placed — thank you!");
      updateCartCount(0);
      setTimeout(()=>{ window.location.href = data.redirect; }, 900);
    }
  });
}

/* ---------------- Product cards: color swatches + add/quick-add ---------------- */
document.querySelectorAll('.card').forEach(card => {
  const id = parseInt(card.dataset.id, 10);

  card.querySelectorAll('.swatch').forEach(sw => {
    sw.addEventListener('click', () => {
      card.querySelectorAll('.swatch').forEach(s => s.classList.remove('selected'));
      sw.classList.add('selected');
    });
  });

  const addBtn = card.querySelector('.add-btn');
  if(addBtn){
    addBtn.addEventListener('click', () => {
      const selected = card.querySelector('.swatch.selected');
      const color = selected ? selected.dataset.color : '#000000';
      addToCart(id, color);
      addBtn.textContent = 'Added ✓';
      addBtn.classList.add('added');
      setTimeout(()=>{ addBtn.textContent = 'Add to Cart'; addBtn.classList.remove('added'); }, 1200);
    });
  }

  const quickBtn = card.querySelector('.quick-add');
  if(quickBtn){
    quickBtn.addEventListener('click', () => {
      const first = card.querySelector('.swatch');
      const color = first ? first.dataset.color : '#000000';
      addToCart(id, color);
    });
  }
});

/* ---------------- Filter + sort (client side, cards already in DOM) ---------------- */
const grid = document.getElementById('productGrid');
let activeCat = 'all';
let sortMode = 'default';

function applyFilterSort(){
  if(!grid) return;
  const cards = Array.from(grid.querySelectorAll('.card'));

  cards.forEach(card => {
    const matches = activeCat === 'all' || card.dataset.cat === activeCat;
    card.style.display = matches ? '' : 'none';
  });

  let visible = cards.filter(c => c.style.display !== 'none');
  if(sortMode === 'low') visible.sort((a,b)=> a.dataset.price - b.dataset.price);
  if(sortMode === 'high') visible.sort((a,b)=> b.dataset.price - a.dataset.price);
  if(sortMode === 'rating') visible.sort((a,b)=> b.dataset.rating - a.dataset.rating);

  visible.forEach(card => grid.appendChild(card));
}

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeCat = chip.dataset.cat;
    applyFilterSort();
  });
});

const sortSelect = document.getElementById('sortSelect');
if(sortSelect){
  sortSelect.addEventListener('change', (e) => {
    sortMode = e.target.value;
    applyFilterSort();
  });
}
