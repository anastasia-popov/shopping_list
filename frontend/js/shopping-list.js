import { CONFIG } from './config.js';

let recentlyDeletedItem = null;
let undoTimeout = null;

async function fetchShoppingList() {
    const response = await fetch(`${CONFIG.API_BASE_URL}/shopping-list`, {
         method: 'GET',
         credentials: 'include'
         });
    const data = await response.json();
    renderShoppingList(data.products);
}

function renderShoppingList(items) {
    const shoppingListContainer = document.getElementById('shopping-list');

    shoppingListContainer.innerHTML = '';
    
    const departments = {};
    items.forEach(item => {
        if (!departments[item.department]) departments[item.department] = [];
            departments[item.department].push(item);
     
    });
    
    for (const department in departments) {
        const section = document.createElement('div');
        section.classList.add('department');
        section.innerHTML = `<h3>${department}</h3>`;
        departments[department].forEach(item => {
            const itemElement = createItemElement(item, false);
            section.appendChild(itemElement);
        });
        shoppingListContainer.appendChild(section);
    }
}

function createItemElement(item, isBought) {
    const div = document.createElement('div');
    div.classList.add('item');
    
    
    //Swipe to remove item
    let startX = 0;
    div.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
    });

    div.addEventListener('touchend', async (e) => {
        const endX = e.changedTouches[0].clientX;
        if (endX - startX > 100) { // Swipe right threshold
            recentlyDeletedItem = item;
            showUndoBanner();
            await removeItem(item);
        }
    });
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.addEventListener('change', () => removeItem(item));
    
    div.appendChild(checkbox);
    div.appendChild(document.createTextNode(`${item.name}`));
    return div;
}

async function removeItem(item) {
    await fetch(`${CONFIG.API_BASE_URL}/shopping-list/remove-product`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: `${item.id}`})
    });
    fetchShoppingList();
    recentlyDeletedItem = item;
    showUndoBanner();
}

window.undoRemove = async function() {
    if (!recentlyDeletedItem) return;
    await fetch(`${CONFIG.API_BASE_URL}/shopping-list/add-product`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name : recentlyDeletedItem.name })
    });
    recentlyDeletedItem = null;
    hideUndoBanner();
    fetchShoppingList();
}

function showUndoBanner() {
    let banner = document.getElementById('undo-banner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'undo-banner';
        banner.style.position = 'fixed';
        banner.style.bottom = '20px';
        banner.style.left = '50%';
        banner.style.transform = 'translateX(-50%)';
        banner.style.background = '#004d40';
        banner.style.color = 'white';
        banner.style.padding = '10px 20px';
        banner.style.borderRadius = '5px';
        banner.style.zIndex = '1000';
          banner.innerHTML = `Item removed. <button style="margin-left:10px;padding:5px;background:white;color:#004d40;border:none;border-radius:3px;cursor:pointer;" onclick="undoRemove()">Undo</button>`;

        document.body.appendChild(banner);

    }
    banner.style.display = 'block';
    
   

    clearTimeout(undoTimeout);
    undoTimeout = setTimeout(() => {
        hideUndoBanner();
        recentlyDeletedItem = null;
    }, 50000);
}

function hideUndoBanner() {
    const banner = document.getElementById('undo-banner');
    if (banner) {
        banner.style.display = 'none';
    }
}


async function addItem(event) {
    event.preventDefault();
    const name = document.getElementById('item-name').value.trim();

    if (!name) return;

    await fetch(`${CONFIG.API_BASE_URL}/shopping-list/add-product`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name : name })
    });

    document.getElementById('add-item-form').reset();
    fetchShoppingList();
}

document.getElementById('add-item-form').addEventListener('submit', addItem);


fetchShoppingList();

